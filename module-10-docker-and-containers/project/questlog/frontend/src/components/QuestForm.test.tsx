/**
 * See lessons/07-frontend-testing-with-vitest-and-rtl.md for the full,
 * line-by-line walkthrough of this file's first test -- every later test
 * in this file (and in ProtectedRoute.test.tsx / QuestListPage.test.tsx)
 * reuses the same three-step shape: **render** the component, **interact**
 * with it the way a real user would (via `userEvent`, never by reaching
 * into React internals), then **assert** on what ended up on screen.
 */
import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QuestForm } from "./QuestForm";

describe("QuestForm", () => {
  it("renders empty, sensible-default fields when creating a new quest", () => {
    render(<QuestForm submitLabel="Add Quest" onSubmit={vi.fn()} />);

    expect(screen.getByLabelText("Title")).toHaveValue("");
    expect(screen.getByLabelText("Description")).toHaveValue("");
    expect(screen.getByLabelText("Quest line")).toHaveValue("");
    expect(screen.getByLabelText("Priority")).toHaveValue("medium");
    expect(screen.getByRole("button", { name: "Add Quest" })).toBeInTheDocument();
  });

  it("pre-fills every field when editing an existing quest", () => {
    render(
      <QuestForm
        submitLabel="Save Changes"
        onSubmit={vi.fn()}
        initialValues={{
          title: "Slay the Dragon",
          description: "A big one.",
          priority: "high",
          questLine: "Main Story",
        }}
      />,
    );

    expect(screen.getByLabelText("Title")).toHaveValue("Slay the Dragon");
    expect(screen.getByLabelText("Priority")).toHaveValue("high");
  });

  it("does not render a Cancel button when no onCancel prop is given", () => {
    render(<QuestForm submitLabel="Add Quest" onSubmit={vi.fn()} />);
    expect(screen.queryByRole("button", { name: "Cancel" })).not.toBeInTheDocument();
  });

  it("calls onCancel when the Cancel button is clicked", async () => {
    const user = userEvent.setup();
    const handleCancel = vi.fn();
    render(<QuestForm submitLabel="Add Quest" onSubmit={vi.fn()} onCancel={handleCancel} />);

    await user.click(screen.getByRole("button", { name: "Cancel" }));

    expect(handleCancel).toHaveBeenCalledTimes(1);
  });

  it("calls onSubmit with the typed-in values when every required field is filled", async () => {
    const user = userEvent.setup();
    const handleSubmit = vi.fn();
    render(<QuestForm submitLabel="Add Quest" onSubmit={handleSubmit} />);

    await user.type(screen.getByLabelText("Title"), "Slay the Dragon");
    await user.type(screen.getByLabelText("Description"), "It has terrorized the village.");
    await user.selectOptions(screen.getByLabelText("Priority"), "high");
    await user.type(screen.getByLabelText("Quest line"), "Main Story");
    await user.click(screen.getByRole("button", { name: "Add Quest" }));

    expect(handleSubmit).toHaveBeenCalledTimes(1);
    expect(handleSubmit).toHaveBeenCalledWith({
      title: "Slay the Dragon",
      description: "It has terrorized the village.",
      priority: "high",
      questLine: "Main Story",
    });
  });

  it("does not call onSubmit when a required field (Title) is left empty", async () => {
    /**
     * This is the "validation" behavior this exercise/lesson set is
     * really about: QuestForm has no hand-written JavaScript validation
     * logic at all (see QuestForm.tsx -- there's no `if (!values.title)`
     * anywhere in it). Every `<input>` simply has a plain HTML `required`
     * attribute. jsdom (the fake browser Vitest renders into --
     * lessons/08's "what jsdom actually is" section) implements the same
     * browser-native "constraint validation" real Chrome/Firefox do:
     * clicking a `type="submit"` button inside a form with an empty
     * `required` field never fires that form's `submit` event at all, so
     * QuestForm's own `handleSubmit` -- and therefore this test's
     * `handleSubmit` prop -- is never called. This is the browser
     * rejecting the submission before any of this app's own code runs,
     * not this component's own logic doing it.
     */
    const user = userEvent.setup();
    const handleSubmit = vi.fn();
    render(<QuestForm submitLabel="Add Quest" onSubmit={handleSubmit} />);

    // Fill in every field EXCEPT the title, then try to submit.
    await user.type(screen.getByLabelText("Description"), "It has terrorized the village.");
    await user.type(screen.getByLabelText("Quest line"), "Main Story");
    await user.click(screen.getByRole("button", { name: "Add Quest" }));

    expect(handleSubmit).not.toHaveBeenCalled();
  });
});
