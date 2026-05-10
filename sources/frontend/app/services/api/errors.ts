export type ProblemKind = "NOT_FOUND" | "ALREADY_EXIST" | "NOT_ALLOWED" | "VALIDATION" | "UNKNOWN";
export type Entity = "USER" | "QUESTION" | "PREDICTION" | "RESOLUTION" | "AUTH" | "UNKNOWN";

export interface ApiErrorPayload {
  type: ProblemKind;
  on: Entity;
  title: string;
  detail: string;
  status: number;
}

export class ApiError extends Error {
  readonly status: number;
  readonly kind: ProblemKind;
  readonly entity: Entity;
  readonly title: string;
  readonly detail: string;

  constructor(payload: ApiErrorPayload) {
    super(payload.detail);
    this.name = "ApiError";
    this.status = payload.status;
    this.kind = payload.type;
    this.entity = payload.on;
    this.title = payload.title;
    this.detail = payload.detail;
  }

  static async fromResponse(response: Response): Promise<ApiError> {
    let payload: ApiErrorPayload;
    try {
      const body = (await response.json()) as Partial<ApiErrorPayload>;
      payload = {
        type: body.type ?? "UNKNOWN",
        on: body.on ?? "UNKNOWN",
        title: body.title ?? response.statusText,
        detail: body.detail ?? `${response.status} ${response.statusText}`,
        status: body.status ?? response.status,
      };
    } catch {
      payload = {
        type: "UNKNOWN",
        on: "UNKNOWN",
        title: response.statusText,
        detail: `${response.status} ${response.statusText}`,
        status: response.status,
      };
    }
    return new ApiError(payload);
  }
}
