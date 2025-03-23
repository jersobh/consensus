from setuptools import setup, find_packages

setup(
    name="llm_consensus",
    version="0.1.0",
    description="Langchain-compatible deliberation and consensus framework using multiple LLMs.",
    author="Jeff Andrade",
    author_email="jersobh@gmail.com",
    packages=find_packages(),
    install_requires=[
        "langchain",
        "langchain_community",
        "pydantic",
        "openai",
        "transformers",
        "torch",
        "ollama"
    ],
    python_requires=">=3.11",
    include_package_data=True,
    license="MIT"
)