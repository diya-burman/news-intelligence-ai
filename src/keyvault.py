import os
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv

load_dotenv()

def get_kv_client():
    credential = ClientSecretCredential(
        tenant_id=os.getenv("TENANT_ID"),
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET")
    )
    return SecretClient(vault_url=os.getenv("KEY_VAULT_URL"), credential=credential)

def get_secrets():
    client = get_kv_client()

    deployment = client.get_secret("interview-openai-deployment-name").value
    model = client.get_secret("interview-openai-model-name").value
    api_key = client.get_secret("interview-openai-model-api-key").value
    endpoint = client.get_secret("interview-openai-model-endpoint").value

    return {
        "deployment": deployment,
        "model": model,
        "api_key": api_key,
        "endpoint": endpoint
    }
if __name__ == "__main__":
    secrets = get_secrets()
    print("✅ Key Vault secrets fetched successfully!")
    print(secrets)