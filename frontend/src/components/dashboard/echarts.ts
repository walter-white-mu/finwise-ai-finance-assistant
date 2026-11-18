import { use, init } from 'echarts/core'
import { BarChart, PieChart } from 'echarts/charts'
import { GridComponent, LegendComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

// Register only the chart types and features used by this dashboard.
use([BarChart, PieChart, GridComponent, LegendComponent, TooltipComponent, CanvasRenderer])

export { init }
