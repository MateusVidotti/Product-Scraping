from asyncio import gather
from datetime import datetime
from httpx import get, AsyncClient, ReadTimeout
import motor.motor_asyncio
from parsel import Selector
from configs.settings import Settings
from scrapper.models import ProductModel, StatusProduto, UpdateProductModel
from scrapper.models import ObjectId

settings = Settings()
client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_url)
db = client.products_db


async def raspa_um_produto(produto_id: ObjectId):
    """
    Raspa os dados de um produto
    """
    produto = await db['produto'].find_one({'_id': ObjectId(str(produto_id))})
    print(produto['url'])
    async with AsyncClient() as http_client:
        try:
         response_produto = await http_client.get(produto['url'], timeout=50, follow_redirects=True)

        except ReadTimeout:
            print('Timeout')
            return ('Timeout')

        if response_produto.status_code != 200:
            print(response_produto.status_code)
            return ('Resposta errada')

        sel_prod = Selector(text=response_produto.content.decode())
        data_str = response_produto.headers.get('date').split(', ')[1]

        try:
            code = int(sel_prod.css('p#barcode_paragraph span::text').get())
        except TypeError:
            code = None
        try:
            barcode = f"{code}({sel_prod.css('p#barcode_paragraph::text').getall()[1].split('(')[1].split(')')[0]})"
        except IndexError:
            barcode = ''

        dados_produto = UpdateProductModel(
            code=code,
            barcode=barcode,
            status=StatusProduto.IMPORTED,
            imported_t=datetime.strptime(data_str, '%d %b %Y %H:%M:%S %Z'),
            product_name=sel_prod.css('h2.title-1::text').get().replace('\xa0', '').split('\n')[0],
            quantity=sel_prod.css('p#field_quantity span.field_value::text').get(),
            categories=', '.join(sel_prod.css('p#field_categories span.field_value a::text').getall()),
            packaging=', '.join(sel_prod.css('p#field_packaging span.field_value a::text').getall()),
            brands=', '.join(sel_prod.css('p#field_brands span.field_value a::text').getall()),
        )
        dados_produto = {k: v for k, v in dados_produto.dict().items() if v is not None}

        update_produto = await db['produto'].update_one({"_id": ObjectId(str(produto_id))}, {"$set": dados_produto})
        print('+ 1 produto raspado')
    return update_produto


async def raspagem_catalogo_produtos(max_paginas=1) -> (list[ProductModel], dict[Exception]):
    """
    Raspa os produtos da página para adquirir as urls
    :param num_paginas: número de páginas para serem extraídas. Esperado 100 produtos por paginas
    :return:
    """
    url_base = 'https://world.openfoodfacts.org/'
    response = get(url_base, timeout=10).content
    sel_prin = Selector(text=response.decode())

    # Encontramos o número de páginas de produtos, onde cada pagina contem 100 produtos.
    paginação = sel_prin.css('ul#pages li :not(#unavailable)::text').getall()
    paginas = range(1, int(paginação[-2]))

    ids_produtos = list()
    urls_produtos_erros = dict()
    for pagina in paginas:
        # para no número maximo de páginas
        if pagina > max_paginas:
            break
        url_pagina = url_base + str(pagina)
        response_pagina = get(url_pagina, timeout=10).content
        sel_pagina = Selector(text=response_pagina.decode())
        li_produtos = sel_pagina.css('ul').css('li').css('a')
        for pagina_produtos in li_produtos:
            if len(pagina_produtos.css('div')) > 0:
                url_produto = url_pagina[:-1] + pagina_produtos.attrib['href']
                # verifica se a url já foi registrada
                produto_registrado = await db['produto'].find_one({'url': url_produto})
                # Cria um novo produto
                if produto_registrado is None:
                    produto = ProductModel(
                        url=url_produto,
                        image_url=pagina_produtos.css('img').attrib['src'].replace('100.jpg', 'full.jpg'),
                        status=StatusProduto.DRAFT
                    )
                    produto = {k: v for k, v in produto.dict().items() if v is not None}
                    novo_produto = await db['produto'].insert_one(produto)
                    ids_produtos.append(novo_produto.inserted_id)
                # Marca para ser atualizado
                else:
                    produto_registrado['status'] = StatusProduto.DRAFT
                    atualiza_status = db['produto'].update_one({'_id': produto_registrado['_id']}, {'$set': {
                        'status': StatusProduto.DRAFT}})
    return ids_produtos, urls_produtos_erros


async def raspar_urls_produtos():
    produtos = await db['produto'].find({'status': StatusProduto.DRAFT}).to_list(None)
    produtos_ids = [p['_id'] for p in produtos]
    grupos_produtos = [produtos_ids[x:x + 10] for x in range(0, len(produtos_ids), 10)]
    for grupo in grupos_produtos:
        await gather(*[raspa_um_produto(_id) for _id in grupo]
        )
        print('proximo grupo')
