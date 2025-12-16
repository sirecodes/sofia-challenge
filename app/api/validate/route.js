const REAL_FLAG = "CTF{TIM3_L34K}";  // Shorter flag (14 chars)
const TIME_DELAY = 150; // 150ms per correct character

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export async function POST(request) {
  try {
    const body = await request.json();
    const submittedFlag = body.flag || "";

    if (!submittedFlag) {
      return Response.json(
        { status: "error", message: "Missing flag parameter" },
        { status: 400 }
      );
    }

    // Character-by-character validation with timing leak
    let correctChars = 0;
    
    for (let i = 0; i < submittedFlag.length; i++) {
      if (i >= REAL_FLAG.length || submittedFlag[i] !== REAL_FLAG[i]) {
        // Wrong character - return immediately with hint
        return Response.json({
          status: "error",
          message: "Incorrect flag",
          hint: `You got ${correctChars} character(s) correct`
        });
      }

      // Correct character - add delay
      correctChars++;
      await sleep(TIME_DELAY);
    }

    // Check if complete
    if (submittedFlag === REAL_FLAG) {
      return Response.json({
        status: "success",
        message: "🎉 Correct flag!"
      });
    }

    // Correct so far but incomplete
    return Response.json({
      status: "partial",
      message: `Correct so far! ${correctChars}/${REAL_FLAG.length} characters found`
    });

  } catch (err) {
    return Response.json(
      { status: "error", message: "Invalid request" },
      { status: 400 }
    );
  }
}