from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from flask_jwt_extended import jwt_required
from models.site import SiteModel

# rota PATH: /hoteis?cidade=Rio de Janeiro&estrelas_min=4&diaria_max=400
class Hoteis(Resource):
 
    # Dados pre definidos (Construtor Local)
    path_params = reqparse.RequestParser() # requerimento (extrair args)
    path_params.add_argument('cidade', type=str, default="",location='args') # argumentos
    path_params.add_argument('estrelas_min', type=float, default=0, location='args') # argumentos
    path_params.add_argument('estrelas_max', type=float, default=0, location='args') # argumentos
    path_params.add_argument('diaria_min', type=float, default=0, location='args') # argumentos
    path_params.add_argument('diaria_max', type=float, default=0, location='args') # argumentos
    path_params.add_argument("itens",type=float, default=10, location="args") # argumentos
    path_params.add_argument("pagina",type=float, default=1, location="args") # argumentos
    '''
    location='args': Indica que o argumento deve ser extraído dos parâmetros da ".query" na URL. 
    Ou seja, ele será lido da parte da URL que vem após o ponto de interrogação (?). 
    Por exemplo, em uma URL como http://exemplo.com/api?diaria_max=100, 
    '''
    
    def get(self):
        meus_filtros = Hoteis.path_params.parse_args()
        query = HotelModel.query # pesquisar por

        # adicionar filtros dinamicamente
        #query = self.adicionar_filtros(query, meus_filtros)
 
        # filtros
        if meus_filtros["cidade"]:
            query = query.filter(HotelModel.cidade == meus_filtros["cidade"])
        if meus_filtros["estrelas_min"]:
            query = query.filter(HotelModel.estrelas >= meus_filtros["estrelas_min"])
        if meus_filtros["estrelas_max"]:
            query = query.filter(HotelModel.estrelas <= meus_filtros["estrelas_max"])
        if meus_filtros["diaria_min"]:
            query = query.filter(HotelModel.diaria >= meus_filtros["diaria_min"])
        if meus_filtros["diaria_max"]:
            query = query.filter(HotelModel.diaria <= meus_filtros["diaria_max"])
        
        # Paginação
        page = meus_filtros['pagina']
        per_page = meus_filtros['itens']
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
 
        # resultado
        resultado_hotel = [hotel.json() for hotel in pagination.items]
 
        return {
            "hoteis": resultado_hotel,
            "quantidade de itens": pagination.total,
            "quantidade de paginas": pagination.pages,
            "pagina atual": page
        }
 
# rota (CRUD)
class Hotel(Resource):
    # Dados pre definidos (Construtor Local)
    atributos = reqparse.RequestParser() # requerimento (extrair args)
    atributos.add_argument('nome', type=str, required=True, help="Falta nome.") # extrair atributo (campo obrigatório)
    atributos.add_argument('estrelas', type=float) # extrair atributo
    atributos.add_argument('diaria', type=float) # extrair atributo
    atributos.add_argument('cidade', type=str) # extrair atributo
    atributos.add_argument('site_id', type=int, required=True, help="Every hotel needs to be linked with a site.") 
    # Solicitar (leitura) por "id"
    def get(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
 
        if hotel:
            return hotel.json()   
        else:
            return {'message': 'Hotel não existe.'}, 404    
    
    # Enviar (criar)
    @jwt_required() # necessário token de acesso
    def post(self, hotel_id): 
        if HotelModel.find_hotel(hotel_id): # retorna alguma coisa ou falso
            return {"message":"Hotel_id '{}' already exists.".format(hotel_id)}, 400
        
        dados = Hotel.atributos.parse_args() 
        hotel = HotelModel(hotel_id, **dados)

        if not SiteModel.find_by_id(dados['site_id']):
            return {'message':'The hotel must be associate to a valid site id.'}, 400
        try:
            hotel.save_hotel()
        except:
            return {"message":"An error occurred trying to create hotel."}, 500
        return hotel.json(), 201      
 
    # Atualizar
    @jwt_required() # necessário token de acesso
    def put(self, hotel_id):
        dados = Hotel.atributos.parse_args()
 
        print(dados)
        hotel = HotelModel.find_hotel(hotel_id) # retorna alguma coisa ou falso
 
        # Se ID existir
        if hotel:
            hotel.update_hotel(**dados) 
 
            hotel.save_hotel() 
 
            return hotel.json(), 200       
        else:
            novo_hotel = HotelModel(hotel_id, **dados)    
            
            novo_hotel.save_hotel() 
 
            return novo_hotel.json()
        
    # Excluir
    @jwt_required() # necessário token de acesso
    def delete(self, hotel_id):
 
        hotel = HotelModel.find_hotel(hotel_id) # retorna alguma coisa ou falso
 
        # Se ID existir
        if hotel:
            hotel.delete_hotel()
            return {'message': 'Hotel deletado.'}, 200   
        else:
            return {'message': 'Hotel não existe.'}, 404

"""
from flask_restful import Resource, reqparse 
from models.hotel import HotelModel
from flask_jwt_extended import jwt_required
import sqlite3

def normalize_path_params(cidade=None,
                          estrelas_min = 0,
                          estrelas_max = 5,
                          diaria_min = 0,
                          diaria_max = 10000,
                          limit = 50,
                          offset = 0, **dados):
    if cidade:
        return {
            'estrelas_min': estrelas_min,
            'estrelas_max': estrelas_max,
            'diaria_min': diaria_min, 
            'diaria_max': diaria_max,
            'cidade': cidade,
            'limit': limit,
            'offset': offset}
    return {
        'estrelas_min': estrelas_min,
        'estrelas_max': estrelas_max,
        'diaria_min': diaria_min, 
        'diaria_max': diaria_max,
        'limit': limit,
        'offset': offset}

path_params = reqparse.RequestParser()
path_params.add_argument('cidade', type=str)
path_params.add_argument('estrelas_min', type=float)
path_params.add_argument('estrelas_max', type=float)
path_params.add_argument('diaria_min', type=float)
path_params.add_argument('diaria_max', type=float)
path_params.add_argument('limit', type=float)
path_params.add_argument('offset', type=float)

class Hoteis(Resource):
    def get(self):
        connection = sqlite3.connect('banco.db')
        cursor = connection.cursor()

        dados = path_params.parse_args()
        dados_validos = {chave:dados[chave] for chave in dados if dados[chave] is not None}
        parametros = normalize_path_params(**dados_validos)

        if not parametros.get('cidade'):
            consulta = "SELECT * FROM hoteis \
            WHERE (estrelas >= ? and estrelas <= ?) \
            and (diaria >= ? and diaria <= ?) \
            LIMIT ? OFFSET ?"
            tupla = tuple([parametros[chave] for chave in parametros])
            resultado = cursor.execute(consulta, tupla)
        else:
            consulta = "SELECT * FROM hoteis \
            WHERE (estrelas >= ? and estrelas <= ?) \
            and (diaria >= ? and diaria <= ?) \
            and cidade = ? LIMIT ? OFFSET ?"
            tupla = tuple([parametros[chave] for chave in parametros])
            resultado = cursor.execute(consulta, tupla)

        hoteis = []
        for linha in resultado:
            hoteis.append({
            'hotel_id': linha[0],
            'nome': linha[1],
            'estrelas': linha[2],
            'diaria': linha[3],
            'cidade': linha[4]
            })

        return {'hoteis': hoteis} # SELECT * FROM Hoteis
   

class Hotel(Resource):
    atributos = reqparse.RequestParser()
    atributos.add_argument('nome', type=str, required=True, help="The field 'nome' cannot be left blank.")
    atributos.add_argument('estrelas', type=float)
    atributos.add_argument('diaria', type=float)
    atributos.add_argument('cidade', type=str)

    def get(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            return hotel.json()
        return {'message': 'Hotel not found.'}, 404 # not found

    @jwt_required()
    def post(self, hotel_id):
        if HotelModel.find_hotel(hotel_id):
            return {"message": "Hotel id '{}' already exists.".format(hotel_id)}, 400 #Bad request

        dados = Hotel.atributos.parse_args()
        hotel = HotelModel(hotel_id, **dados)
        try:
            hotel.save_hotel()
        except:
            return {"message": "An error ocurred trying to create hotel."}, 500 #Internal save error
        return hotel.json(), 201

    @jwt_required()
    def put(self, hotel_id):  
        dados = Hotel.atributos.parse_args()
        hotel = HotelModel(hotel_id, **dados)

        hotel_encontrado = HotelModel.find_hotel(hotel_id)
        if hotel_encontrado:
            hotel_encontrado.update_hotel(**dados)
            hotel_encontrado.save_hotel()
            return hotel_encontrado.json(), 200 #OK
        hotel.save_hotel()
        return hotel.json(), 201 # created criado

    @jwt_required()
    def delete(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            hotel.delete_hotel()
            return {'message': 'Hotel deleted.'}
        return {'message': 'Hotel not found.'}, 404
"""