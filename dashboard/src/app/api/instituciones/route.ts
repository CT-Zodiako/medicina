import { NextResponse } from "next/server";

const PREDICTION_API_URL = process.env.PREDICTION_API_URL ?? "http://127.0.0.1:8001";

/** Proxies the scenario-A institution list (code + name) for the selector. */
export async function GET() {
  let upstream: Response;
  try {
    upstream = await fetch(`${PREDICTION_API_URL}/instituciones`);
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
