from scrapy.item import Item, Field

class AcordaoItem(Item):
    acordaoId   = Field()
    acordaoType = Field()
    localSigla  = Field()
    local       = Field()
    cabecalho   = Field()
    publicacao  = Field()
    dataPublic  = Field()
    relator     = Field()
    orgaoJulg   = Field()
    dataJulg    = Field()
    fontePublic = Field()
    ementa      = Field()
    decisao     = Field()
    citacoes    = Field()
    legislacao  = Field()
    legislacaoTexto  = Field()
    observacao  = Field()
    doutrinas   = Field()
    resumo      = Field()
    tags        = Field()
    partes      = Field()
    partesTexto = Field()
    tribunal    = Field()
    index       = Field()
    notas       = Field()
    similaresTexto = Field()
    similares   = Field()

class LawItem(Item):
    sigla  = Field()
    descricao = Field()
    tipo   = Field()
    ano    = Field()
    refs   = Field()
