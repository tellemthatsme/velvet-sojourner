from setuptools import setup, find_packages

long_description = open("README.md", encoding="utf-8").read()

setup(
    name="chatgpt-exporter",
    version="2.0.0",
    description="Export, analyze, and own AI conversations from ChatGPT, Claude, and Gemini",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Velvet Sojourner",
    author_email="dev@velvet-sojourner.dev",
    url="https://github.com/velvet-sojourner/chatgpt-exporter",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    packages=find_packages(include=['src', 'src.*']),
    include_package_data=True,
    package_data={
        'src.web': ['templates/*', 'static/*'],
    },
    py_modules=["cli"],
    python_requires=">=3.9",
    install_requires=[
        "pypdf>=3.0.0",
        "beautifulsoup4>=4.12.0",
        "python-frontmatter>=1.0.0",
        "python-dotenv>=1.0.0",
        "openai>=1.0.0",
        "anthropic>=0.30.0",
        "python-multipart>=0.0.5",
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.20.0",
        "jinja2>=3.0.0",
    ],
    extras_require={
        "ml": ["sentence-transformers>=2.2.0"],
        "gui": ["PyQt6>=6.5.0"],
        "pdf": ["weasyprint>=60.0"],
        "dev": ["pytest>=7.0.0"],
    },
    entry_points={
        'console_scripts': [
            'chatgpt-exporter=cli:cli_main',
        ],
    },
)
