FROM python:3.11-slim

WORKDIR /app

# Install OS build deps needed to build some Python packages (tokenizers, etc.)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	   build-essential \
	   gcc \
	   g++ \
	   curl \
	   git \
	   pkg-config \
	   libcairo2 \
	   libgdk-pixbuf-2.0-0 \
	   libglib2.0-0 \
	   libpango-1.0-0 \
	   libpangocairo-1.0-0 \
	   libssl-dev \
	   libffi-dev \
	   shared-mime-info \
	&& rm -rf /var/lib/apt/lists/*

# Install Rust toolchain via rustup (reliable cargo/rustc availability)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
	&& . $HOME/.cargo/env \
	&& rustup default stable

# Ensure cargo is on PATH for subsequent steps
ENV PATH="/root/.cargo/bin:${PATH}"

# Ensure pip, wheel and setuptools are recent so pip can use manylinux wheels when available
RUN python -m pip install --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
