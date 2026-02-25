type AnyRecord = Record<string, any>;

const toRecord = (value: unknown): AnyRecord =>
  value && typeof value === "object" && !Array.isArray(value)
    ? (value as AnyRecord)
    : {};

const coalesceRecord = (...candidates: unknown[]): AnyRecord => {
  for (const candidate of candidates) {
    if (candidate && typeof candidate === "object" && !Array.isArray(candidate)) {
      return candidate as AnyRecord;
    }
  }
  return {};
};

export const normalizeAnalysisPayload = (project?: unknown): AnyRecord => {
  const projectRecord = toRecord(project);
  const rawAnalysis = toRecord(projectRecord.analysis);
  const calculations = coalesceRecord(
    rawAnalysis.calculations,
    projectRecord.calculation_data,
    projectRecord.calculations,
    projectRecord
  );
  const parsedInput = coalesceRecord(
    rawAnalysis.parsed_input,
    toRecord(rawAnalysis.request_payload).parsed_input,
    projectRecord.parsed_input,
    projectRecord.form_state,
    projectRecord.form_inputs
  );

  return {
    ...rawAnalysis,
    parsed_input: parsedInput,
    calculations,
  };
};
