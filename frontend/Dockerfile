# Use an official Node runtime as a parent image
FROM node:18-alpine

# Set the working directory in the container to /app
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install app dependencies
RUN npm install

# Add execute permissions to the react-scripts command
RUN chmod +x /app/node_modules/.bin/react-scripts

# Copy the rest of the application code
COPY . .

# Make port 3000 available
EXPOSE 3000

# Run the app when the container launches
CMD ["npm", "start"]