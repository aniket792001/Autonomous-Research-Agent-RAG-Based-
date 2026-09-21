from langchain_community.document_loaders import PyPDFLoader

def load_documents(path):
    loader = PyPDFLoader(path)
    return loader.load()
