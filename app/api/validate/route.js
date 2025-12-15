const REAL_FLAG = "SENT1NEL_OBS3RV3S";
const TIME_DELAY = 100; // Increased from 50ms to 100ms

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export async function POST(request) {
  try {
    const body = await request.json();
    const submittedFlag = body.flag || "";

    if (!submittedFlag) {
      return Response.json(
        { status: "error", message: "Invalid request. 'flag' missing." },
        { status: 400 }
      );
    }

    // Character-by-character comparison with timing leak
    for (let i = 0; i < submittedFlag.length; i++) {
      if (i >= REAL_FLAG.length || submittedFlag[i] !== REAL_FLAG[i]) {
        // Wrong character - return immediately
        return Response.json({
          status: "error",
          message: "Validation failed",
          position: i // Helpful for debugging (optional)
        });
      }

      // ⏱️ Intentional timing leak - delay AFTER each correct character
      await sleep(TIME_DELAY);
    }

    // Check if complete
    if (submittedFlag === REAL_FLAG) {
      return Response.json({
        status: "success",
        message: "Flag Correct! 🎉"
      });
    }

    // Correct so far but incomplete
    return Response.json({
      status: "partial",
      message: "Keep going...",
      length: submittedFlag.length
    });

  } catch (err) {
    return Response.json(
      { status: "error", message: "Bad JSON" },
      { status: 400 }
    );
  }
}