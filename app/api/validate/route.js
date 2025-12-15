const REAL_FLAG = "SENT1NEL_OBS3RV3S";
const TIME_DELAY = 50; // ms

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

    for (let i = 0; i < submittedFlag.length; i++) {
      if (
        i >= REAL_FLAG.length ||
        submittedFlag[i] !== REAL_FLAG[i]
      ) {
        return Response.json({
          status: "error",
          message: "Validation failed"
        });
      }

      // ⏱️ Intentional timing leak
      await sleep(TIME_DELAY);
    }

    if (submittedFlag === REAL_FLAG) {
      return Response.json({
        status: "success",
        message: "Flag Correct!"
      });
    }

    return Response.json({
      status: "partial",
      message: "Keep going..."
    });

  } catch (err) {
    return Response.json(
      { status: "error", message: "Bad JSON" },
      { status: 400 }
    );
  }
}
