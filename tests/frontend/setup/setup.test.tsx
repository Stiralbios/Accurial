import { describe, expect, it } from "vitest";

import { renderWithProviders } from "../setup/render";

describe("test setup smoke", () => {
  it("renders a simple component within providers", () => {
    const { getByText } = renderWithProviders(<div>hello</div>);
    expect(getByText("hello")).toBeInTheDocument();
  });
});
