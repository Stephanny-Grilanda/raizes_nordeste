import enum

class CanalPedido(str, enum.Enum):
    APP = "APP"
    TOTEM = "TOTEM"
    BALCAO = "BALCAO"
    WEB = "WEB"

class StatusPedido(str, enum.Enum):
    PENDENTE = "PENDENTE"
    PAGO = "PAGO"
    PREPARACAO = "PREPARACAO"
    PRONTO = "PRONTO"
    CANCELADO = "CANCELADO"

class TipoFuncionario(str, enum.Enum):
    ADMIN = "ADMIN"
    GERENTE = "GERENTE"
    ATENDENTE = "ATENDENTE"
    COZINHA = "COZINHA"

class StatusPagamento(str, enum.Enum):
    PAGO = "PAGO"
    RECUSADO = "RECUSADO"

class MetodoPagamento(str, enum.Enum):
    PIX = "PIX"
    DEBITO = "DEBITO"
    CREDITO = "CREDITO"
    DINHEIRO = "DINHEIRO"