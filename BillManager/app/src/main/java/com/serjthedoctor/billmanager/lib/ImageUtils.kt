package com.serjthedoctor.billmanager.lib

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Matrix
import android.util.Log
import androidx.exifinterface.media.ExifInterface
import java.io.File

class ImageUtils {
    companion object {
        const val TAG = "ImageUtils"

        fun ensurePortraitImageFile(file: File) {
            val bitmap = BitmapFactory.decodeFile(file.path)
            val orientation: Int = ExifInterface(file.path).getAttributeInt(
                ExifInterface.TAG_ORIENTATION,
                ExifInterface.ORIENTATION_UNDEFINED
            )

            Log.d(TAG, "Orientation $orientation")

            val rotatedBitmap = when (orientation) {
                ExifInterface.ORIENTATION_ROTATE_90 -> rotateBitmap(bitmap, 90f)
                ExifInterface.ORIENTATION_ROTATE_180 -> rotateBitmap(bitmap, 180f)
                ExifInterface.ORIENTATION_ROTATE_270 -> rotateBitmap(bitmap, 270f)
                ExifInterface.ORIENTATION_NORMAL -> bitmap
                else -> bitmap
            }

            Log.d(TAG, "Successfully rotated bitmap")

            val fileStream = file.outputStream()
            rotatedBitmap.compress(Bitmap.CompressFormat.JPEG, 100, fileStream)
            fileStream.close()
        }

        private fun rotateBitmap(source: Bitmap, angle: Float): Bitmap {
            val matrix = Matrix()
            matrix.postRotate(angle)
            Log.d(TAG, "Rotating bitmap with $angle")
            return Bitmap.createBitmap(source, 0, 0, source.width, source.height,
                    matrix, false)
        }
    }
}