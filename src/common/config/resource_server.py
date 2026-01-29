from pydantic_settings import BaseSettings


class ResourceServerConfig(BaseSettings):
    RESOURCE_SERVER_BASE_URL: str
    #env에 이거 추가하면 됨
    # ex) RESOURCE_SERVER_BASE_URL=https:// ···