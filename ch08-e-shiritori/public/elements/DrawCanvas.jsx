import { useRef, useState, useEffect } from "react";
import { Button } from "@/components/ui/button";

export default function DrawCanvas() {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [penColor, setPenColor] = useState("#000000");
  const [penSize, setPenSize] = useState(4);
  const [submitted, setSubmitted] = useState(false);

  const hint = props.hint || "絵を描いてね！";
  const round = props.round || 1;
  const maxRounds = props.maxRounds || 5;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    setSubmitted(false);
  }, [props.hint]);

  const getPos = (e, canvas) => {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    if (e.touches) {
      return {
        x: (e.touches[0].clientX - rect.left) * scaleX,
        y: (e.touches[0].clientY - rect.top) * scaleY,
      };
    }
    return {
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top) * scaleY,
    };
  };

  const startDraw = (e) => {
    if (submitted) return;
    e.preventDefault();
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const pos = getPos(e, canvas);
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
    setIsDrawing(true);
  };

  const draw = (e) => {
    if (!isDrawing || submitted) return;
    e.preventDefault();
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const pos = getPos(e, canvas);
    ctx.lineWidth = penSize;
    ctx.lineCap = "round";
    ctx.strokeStyle = penColor;
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();
  };

  const stopDraw = (e) => {
    if (e) e.preventDefault();
    setIsDrawing(false);
  };

  const clearCanvas = () => {
    if (submitted) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  };

  const submit = () => {
    if (submitted) return;
    const canvas = canvasRef.current;
    const imageData = canvas.toDataURL("image/png");
    setSubmitted(true);
    callAction({ name: "submit_drawing", payload: { image: imageData } });
  };

  return (
    <div className="flex flex-col items-center gap-3 p-4 bg-card rounded-xl border shadow-sm w-full max-w-md">
      <div className="flex items-center justify-between w-full">
        <span className="text-sm font-semibold text-muted-foreground">
          ラウンド {round} / {maxRounds}
        </span>
        <span className="text-sm font-medium text-primary">{hint}</span>
      </div>

      <canvas
        ref={canvasRef}
        width={400}
        height={400}
        className="border-2 border-border rounded-lg bg-white cursor-crosshair touch-none w-full"
        style={{ maxWidth: "400px", aspectRatio: "1 / 1" }}
        onMouseDown={startDraw}
        onMouseMove={draw}
        onMouseUp={stopDraw}
        onMouseLeave={stopDraw}
        onTouchStart={startDraw}
        onTouchMove={draw}
        onTouchEnd={stopDraw}
      />

      <div className="flex items-center gap-3 w-full flex-wrap">
        <label className="flex items-center gap-1 text-sm">
          <span>色：</span>
          <input
            type="color"
            value={penColor}
            onChange={(e) => setPenColor(e.target.value)}
            className="w-8 h-8 rounded cursor-pointer border"
            disabled={submitted}
          />
        </label>
        <label className="flex items-center gap-1 text-sm">
          <span>太さ：</span>
          <input
            type="range"
            min="1"
            max="20"
            value={penSize}
            onChange={(e) => setPenSize(Number(e.target.value))}
            className="w-20"
            disabled={submitted}
          />
          <span className="w-4">{penSize}</span>
        </label>
      </div>

      <div className="flex gap-2 w-full">
        <Button
          variant="outline"
          onClick={clearCanvas}
          disabled={submitted}
          className="flex-1"
        >
          🗑️ クリア
        </Button>
        <Button
          onClick={submit}
          disabled={submitted}
          className="flex-1"
        >
          {submitted ? "送信済み ✅" : "送る 🎨"}
        </Button>
      </div>
    </div>
  );
}
