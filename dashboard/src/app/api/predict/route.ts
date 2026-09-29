import { NextResponse } from "next/server";

const PREDICTION_API_URL = process.env.PREDICTION_API_URL ?? "http://127.0.0.1:8001";

/**
 * Proxies to the local FastAPI service (api_2021_2024/main.py) so the
 * browser never talks cross-origin to the Python process directly.
 */
export async function POST(request: Request) {
  const body = await request.json();

  let upstream: Response;
  try {
    upstream = await fetch(`${PREDICTION_API_URL}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    return NextResponse.json(
      {
        error:
          "No se pudo conectar con la API de predicción. ¿Está corriendo " +
          "`uvicorn api_2021_2024.main:app --port 8001` desde la raíz del repo?",
      },
      { status: 503 },
    );
  }

  const data = await upstream.json();
  return NextResponse.json(data, { status: upstream.status });
}

export async function GET() {
  let upstream: Response;
  try {
    upstream = await fetch(`${PREDICTION_API_URL}/metadata`);
  } catch {
    return NextResponse.json(
      {
        error:
          "No se pudo conectar con la API de predicción. ¿Está corriendo " +
          "`uvicorn api_2021_2024.main:app --port 8001` desde la raíz del repo?",
      },
      { status: 503 },
    );
  }
  const data = await upstream.json();
  return NextResponse.json(data, { status: upstream.status });
}
