package com.serjthedoctor.billmanager.adapter

import android.graphics.Color
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.serjthedoctor.billmanager.R
import com.serjthedoctor.billmanager.domain.Item
import kotlin.math.abs

class ItemsAdapter : RecyclerView.Adapter<ItemsAdapter.ItemsViewHolder>() {
    private var items = mutableListOf<Item>()

    inner class ItemsViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val namee: TextView = view.findViewById(R.id.deItemName)
        val quantity: TextView = view.findViewById(R.id.deItemQuantity)
        val unit: TextView = view.findViewById(R.id.deItemUnit)
        val unitPrice: TextView = view.findViewById(R.id.deItemUnitPrice)
        val price: TextView = view.findViewById(R.id.deItemPrice)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ItemsViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.items_list_item, parent, false)
        return ItemsViewHolder(view)
    }

    override fun onBindViewHolder(holder: ItemsViewHolder, position: Int) {
        val item = items[position]

        holder.namee.text = item.name
        holder.quantity.text = item.quantity.toString()
        holder.unit.text = item.unit
        holder.unitPrice.text = item.unitPrice.toString()
        holder.price.text = item.price.toString()

        reColor(holder)

        holder.namee.setOnKeyListener { _, _, _ ->
            item.name = holder.namee.text.toString()
            false
        }
        holder.quantity.setOnKeyListener { _, _, _ ->
            if (!holder.quantity.text.isNullOrBlank()) {
                item.quantity = holder.quantity.text.toString().toFloat()
                reColor(holder)
            }
            false
        }
        holder.unit.setOnKeyListener { _, _, _ ->
            item.unit = holder.unit.text.toString()
            false
        }
        holder.unitPrice.setOnKeyListener { _, _, _ ->
            if (!holder.unitPrice.text.isNullOrBlank()) {
                item.unitPrice = holder.unitPrice.text.toString().toFloat()
                reColor(holder)
            }
            false
        }
        holder.price.setOnKeyListener { _, _, _ ->
            if (!holder.price.text.isNullOrBlank()) {
                item.price = holder.price.text.toString().toFloat()
                reColor(holder)
            }
            false
        }
    }

    override fun getItemCount(): Int = items.size

    fun setItems(newItems: List<Item>) {
        items.clear()
        items.addAll(newItems)
        notifyDataSetChanged()
    }

    private fun reColor(holder: ItemsViewHolder) {
        try {
            val quantity = holder.quantity.text.toString().toFloat()
            val unitPrice = holder.unitPrice.text.toString().toFloat()
            val price = holder.price.text.toString().toFloat()

            if (abs(quantity * unitPrice - price) > 0.5) {
                holder.price.setTextColor(Color.RED)
            } else {
                holder.price.setTextColor(Color.BLACK)
            }
        } catch (e: Exception) {
            e.message?.let { Log.e("[ItemsAdapter]", it, e) }
        }
    }
}