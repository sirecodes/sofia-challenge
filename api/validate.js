export default async function handler(req, res) {
  const REAL_FLAG = "CREED{FUZZ1NG_D0N3}";
  const TIME_DELAY = 50; // ms

  if (req.method !== "POST") {
    return res
      .status(405)
      .json({ status: "error", message: "Method not allowed" });
  }

  const submittedFlag = req.body?.flag;

  if (!submittedFlag) {
    return res
      .status(400)
      .json({ status: "error", message: "Invalid request. 'flag' field missing." });
  }

  for (let i = 0; i < submittedFlag.length; i++) {
    if (i >= REAL_FLAG.length || submittedFlag[i] !== REAL_FLAG[i]) {
      return res.json({ status: "error", message: "Validation failed" });
    }

    // ⏱️ Intentional timing leak
    await new Promise(resolve => setTimeout(resolve, TIME_DELAY));
  }

  if (submittedFlag === REAL_FLAG) {
    return res.json({ status: "success", message: "Flag Correct!" });
  }

  return res.json({ status: "partial", message: "Keep going..." });
}
