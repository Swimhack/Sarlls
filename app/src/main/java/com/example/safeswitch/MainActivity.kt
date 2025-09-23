package com.example.safeswitch

import android.os.Bundle
import android.widget.RelativeLayout
import android.widget.Switch
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat

class MainActivity : AppCompatActivity() {

    private lateinit var toggleSwitch: Switch
    private lateinit var statusText: TextView
    private lateinit var rootLayout: RelativeLayout

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        toggleSwitch = findViewById(R.id.safeSwitch)
        statusText = findViewById(R.id.statusText)
        rootLayout = findViewById(R.id.rootLayout)

        toggleSwitch.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) {
                statusText.text = "Battery is connected"
                statusText.setBackgroundResource(R.drawable.status_background_green)
                rootLayout.setBackgroundColor(ContextCompat.getColor(this, R.color.green))
            } else {
                statusText.text = "Battery is disconnected"
                statusText.setBackgroundResource(R.drawable.status_background_red)
                rootLayout.setBackgroundColor(ContextCompat.getColor(this, R.color.red))
            }
        }
    }
}
