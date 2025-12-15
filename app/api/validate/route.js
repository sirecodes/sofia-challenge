const REAL_FLAG = "SENT1NEL_OBS3RV3S";
const TIME_DELAY = 100; // milliseconds

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export async function POST(request) {
  try {
    const body = await request.json();
    const submittedFlag = body.flag;
    const checkByte = body.checkByte;
    const position = body.position;

    // Mode 1: Binary search mode (new!)
    if (checkByte !== undefined && position !== undefined) {
      // Validate position
      if (position >= REAL_FLAG.length) {
        return Response.json({ 
          status: "error", 
          message: "Position out of range" 
        });
      }

      const realCharCode = REAL_FLAG.charCodeAt(position);
      
      // ⏱️ TIMING LEAK: Delay if the guess is <= the actual character
      if (checkByte <= realCharCode) {
        await sleep(TIME_DELAY);
      }
      
      return Response.json({
        status: "binary_check",
        message: "Check complete"
      });
    }

    // Mode 2: Traditional validation mode (for final verification)
    if (submittedFlag !== undefined) {
      // Character-by-character validation
      for (let i = 0; i < submittedFlag.length; i++) {
        if (i >= REAL_FLAG.length || submittedFlag[i] !== REAL_FLAG[i]) {
          return Response.json({
            status: "error",
            message: "Validation failed",
            correctLength: i
          });
        }
        await sleep(TIME_DELAY);
      }

      // Check if complete
      if (submittedFlag === REAL_FLAG) {
        return Response.json({
          status: "success",
          message: "🎉 Flag Correct!"
        });
      }

      return Response.json({
        status: "partial",
        message: "Keep going...",
        length: submittedFlag.length
      });
    }

    // Invalid request
    return Response.json(
      { status: "error", message: "Invalid request - missing parameters" },
      { status: 400 }
    );

  } catch (err) {
    return Response.json(
      { status: "error", message: "Bad JSON" },
      { status: 400 }
    );
  }
}