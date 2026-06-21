import { useEffect, useState } from "react";
import { fetchConcepts, submitAnswer } from "../api.js";

const EMPTY_FORM = {
  concept_key: "",
  question_text: "",
  student_answer: "",
  correct_answer: "",
  is_correct: false,
};

export default function AnswerSubmitForm({ studentId, onSubmitted }) {
  const [concepts, setConcepts] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchConcepts().then((data) => {
      setConcepts(data);
      if (data.length > 0) {
        setForm((f) => ({ ...f, concept_key: data[0].concept_key }));
      }
    });
  }, []);

  const update = (field) => (e) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    try {
      const result = await submitAnswer({ student_id: studentId, ...form });
      onSubmitted?.(result);
      setForm((f) => ({ ...EMPTY_FORM, concept_key: f.concept_key }));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="answer-form" onSubmit={handleSubmit}>
      {/*
        This is a real curriculum standard, not free text — pulled live
        from GET /api/concepts, which reads curriculum_standards.py.
        Same source of truth on both ends, so labeling can never drift.
      */}
      <select value={form.concept_key} onChange={update("concept_key")} required>
        {concepts.map((c) => (
          <option key={c.concept_key} value={c.concept_key}>
            {c.subject} · {c.standard_code}
          </option>
        ))}
      </select>

      <input
        placeholder="question text"
        value={form.question_text}
        onChange={update("question_text")}
        required
      />
      <div className="answer-form-row">
        <input
          placeholder="student's answer"
          value={form.student_answer}
          onChange={update("student_answer")}
          required
        />
        <input
          placeholder="correct answer"
          value={form.correct_answer}
          onChange={update("correct_answer")}
          required
        />
      </div>
      <label className="answer-form-checkbox">
        <input
          type="checkbox"
          checked={form.is_correct}
          onChange={(e) => setForm((f) => ({ ...f, is_correct: e.target.checked }))}
        />
        student got this right
      </label>
      <button type="submit" disabled={submitting}>
        {submitting ? "Submitting..." : "Submit answer"}
      </button>
    </form>
  );
}
