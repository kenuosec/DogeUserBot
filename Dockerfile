# Get Docker image
FROM sandy1709/catuserbot:slim-buster

# Clone Doge repository + work directory + minor adjustment
RUN git clone https://github.com/DOG-E/DogeUserBot.git /usr/src/DogeUserBot
WORKDIR /usr/src/DogeUserBot
ENV PATH="/usr/src/DogeUserBot/bin:$PATH"

# Install requirements
RUN pip3 install --no-cache-dir -U -r requirements.txt

# Run Doge
RUN chmod a+x doger
CMD ["./doger"]