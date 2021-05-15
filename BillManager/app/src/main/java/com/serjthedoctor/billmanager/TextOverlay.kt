package com.serjthedoctor.billmanager

import android.content.Context
import android.graphics.*
import android.util.AttributeSet
import android.util.Log
import android.view.View
import com.google.mlkit.vision.text.Text

class TextOverlay(context: Context, attrs: AttributeSet) : View(context, attrs) {
    private var rectangle = Rect(10, 10, width - 10, height - 10)
    private var recognizedData: List<Text.TextBlock>? = null
    private var paint = Paint()
    private var canvas: Canvas? = null
    private var heightScaleFactor = 1F
    private var widthScaleFactor = 1F

    override fun onDraw(canvas: Canvas?) {
        super.onDraw(canvas)
        this.canvas = canvas
        Log.d(ReceiptScannerActivity.TAG, "TEXTOVERLAY DRAWN")
        // canvas?.scale(3F, 4F)

        paint.color = Color.GREEN
        paint.strokeWidth = 3F
        paint.style = Paint.Style.STROKE
        paint.flags = Paint.ANTI_ALIAS_FLAG
        paint.textSize = 35F
        //canvas?.drawText("Height: $height", width - 300F, 100F, paint)
        //canvas?.drawText("Width: $width", width - 300F, 150F, paint)

        // recognizedData?.forEach(this::plotTextBlock)
        recognizedData?.forEach { textBlock ->
            textBlock.lines.forEach(this::plotTextLine)
        }

        // debugDrawing()
    }

    private fun debugDrawing() {
        val debugPaint = Paint().apply {
            color = Color.RED
            strokeWidth = 3f
            style = Paint.Style.STROKE
            textSize = 35f
        }
        var xOffset = 0
        while (xOffset < width) {
            canvas?.drawLine(xOffset.toFloat(), 0f, xOffset.toFloat(), height.toFloat(), debugPaint)
            canvas?.drawText((xOffset/100).toString(), xOffset.toFloat(), 50f, debugPaint)
            xOffset += 100
        }
        var yOffset = 0f
        while (yOffset < height) {
            canvas?.drawLine(0f, yOffset, width.toFloat(), yOffset, debugPaint)
            canvas?.drawText((yOffset/100).toString(), 5f, yOffset, debugPaint)
            yOffset += 200
        }
    }

    private fun plotTextBlock(textBlock: Text.TextBlock) {
        val box = textBlock.boundingBox
        canvas?.drawRect(processRect(textBlock.boundingBox), paint)
        val text = textBlock.text + " (${box?.left}, ${box?.top}, ${box?.right}, ${box?.bottom})"
        canvas?.drawText(text, box?.left!!.toFloat(), -15F + box.top, paint)
    }

    private fun plotTextLine(line: Text.Line) {
        val box = line.boundingBox
        canvas?.drawRect(processRect(box), paint)
        val text = line.text + " (${box?.left}, ${box?.top}, ${box?.right}, ${box?.bottom})"
        canvas?.drawText(text, box?.left!!.toFloat(), -15F + box.top, paint)
    }

    private fun processRect(rect: Rect?): Rect {
        val r = rect ?: Rect()

        r.left = (r.left* widthScaleFactor).toInt()
        r.top = (r.top * heightScaleFactor).toInt()
        r.right = (r.right * widthScaleFactor).toInt()
        r.bottom = (r.bottom * heightScaleFactor).toInt()

        return r
    }

    fun setRecognizedData(data: List<Text.TextBlock>, dataHeight: Int, dataWidth: Int) {
        recognizedData = data
        heightScaleFactor = height.toFloat() / dataWidth
        widthScaleFactor = width.toFloat() / dataHeight
        Log.d(ReceiptScannerActivity.TAG, "Set data size ${data.size}")
        Log.d(ReceiptScannerActivity.TAG, "Height: $height, DataWidth: $dataWidth => $heightScaleFactor")
        Log.d(ReceiptScannerActivity.TAG, "Width: $width, DataHeight: $dataHeight => $widthScaleFactor")
        invalidate()
    }
}