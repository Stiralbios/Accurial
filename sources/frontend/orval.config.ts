import { defineConfig } from "orval";

export default defineConfig({
  accurial: {
    input: {
      target: process.env.OPENAPI_URL ?? "http://localhost:8800/openapi.json",
    },
    output: {
      mode: "tags-split",
      target: "./app/services/api/generated/index.ts",
      schemas: "./app/services/api/generated/model",
      client: "react-query",
      mock: true,
      prettier: true,
      clean: true,
      override: {
        mutator: {
          path: "./app/services/api/client.ts",
          name: "apiFetch",
        },
        query: {
          useQuery: true,
          useMutation: true,
          signal: true,
        },
      },
    },
  },
});
