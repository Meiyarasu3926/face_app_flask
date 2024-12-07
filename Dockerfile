# Use an official Debian base image
FROM debian:bookworm

# Set environment variables to avoid prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Update system and install necessary dependencies
RUN echo "deb http://deb.debian.org/debian bookworm main" > /etc/apt/sources.list \
    && echo "deb http://deb.debian.org/debian bookworm-updates main" >> /etc/apt/sources.list \
    && echo "deb http://security.debian.org/debian-security bookworm-security main" >> /etc/apt/sources.list \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && apt-get update --fix-missing -o Acquire::Retries=3 \
    && apt-get install -y --no-install-recommends \
       libssl-dev \
       build-essential \
       curl \
       wget \
       software-properties-common \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*





# Install Python and pip
RUN apt-get update -o Acquire::Retries=3 \
    && apt-get install -y python3 python3-pip \
    && pip3 install --upgrade pip

# Create a working directory
WORKDIR /app

# Copy requirements.txt file (if present) to the container
COPY requirements.txt /app/

# Install Python dependencies
RUN if [ -f "requirements.txt" ]; then pip3 install -r requirements.txt; fi

# Copy the rest of the application files
COPY . /app/

# Expose the port the app runs on
EXPOSE 8080

# Run the application (replace `app.py` with your app's entry point)
CMD ["python3", "app.py"]
