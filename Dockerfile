FROM node:20-slim AS frontend-build

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY backend/ ./backend/
COPY main.py ./

# Copy built frontend
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Railway uses PORT env var
ENV PORT=8080
EXPOSE 8080

# Start command - uses shell to expand $PORT
CMD sh -c "python -m uvicorn backend.main:app --host 0.0.0.0 --port \$PORT"
