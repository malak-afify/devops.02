
FROM python:3.9-slim AS builder

WORKDIR /fintech

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ==========================================
# Stage 2: Final Light Image
# ==========================================
FROM python:3.9-slim

WORKDIR /fintech

COPY --from=builder /root/.local /root/.local
COPY app.py .

ENV PATH=/root/.local/bin:$PATH

EXPOSE 5000

CMD ["python", "app.py"]
