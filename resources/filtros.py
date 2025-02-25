from models.hotel import HotelModel
from hotel import Hoteis

def adicionar_filtros(query, filtros):   
    # filtros
    if filtros["cidade"]:
        query = query.filter(HotelModel.cidade == filtros["cidade"])
    if filtros["estrelas_min"]:
        query = query.filter(HotelModel.estrelas >= filtros["estrelas_min"])
    if filtros["estrelas_max"]:
        query = query.filter(HotelModel.estrelas <= filtros["estrelas_max"])
    if filtros["diaria_min"]:
        query = query.filter(HotelModel.diaria >= filtros["diaria_min"])
    if filtros["diaria_max"]:
        query = query.filter(HotelModel.diaria <= filtros["diaria_max"])
    return query