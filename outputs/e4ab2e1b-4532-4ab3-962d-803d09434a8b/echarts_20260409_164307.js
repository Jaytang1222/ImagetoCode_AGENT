var chartDom = document.getElementById('main');
var myChart = echarts.init(chartDom);
var option;

// 辅助函数：生成指定范围内的随机数据
function generateData(count, xMin, xMax, yMin, yMax) {
    var data = [];
    for (var i = 0; i < count; i++) {
        var x = Math.random() * (xMax - xMin) + xMin;
        var y = Math.random() * (yMax - yMin) + yMin;
        // 添加一些正态分布的倾向，让数据更聚集
        if (Math.random() > 0.5) {
             x = x * 0.8 + (xMin + xMax) / 2 * 0.2;
             y = y * 0.8 + (yMin + yMax) / 2 * 0.2;
        }
        data.push([x, y]);
    }
    return data;
}

// 定义颜色
var colors = {
    CD: '#A6DCEF', // 浅蓝
    BD: '#006D8C', // 深青
    AD: '#9FD668', // 浅绿
    CF: '#0073C6', // 深蓝
    BF: '#9E9E9E', // 灰
    AF: '#FACFA0'  // 浅橙
};

// 生成模拟数据以复现分布形态
// CD: 左上 (x<0, y>0)
var dataCD = generateData(35, -30, -5, 0.5, 4);
// BD: 中上 (x~0, y>0)
var dataBD = generateData(80, -2, 2, 0, 3);
// AD: 右上 (x>0, y>0) - 最分散
var dataAD = generateData(146, 5, 80, 0, 10);
// CF: 左下 (x<0, y<0) - 最密集
var dataCF = generateData(215, -30, -5, -6, -0.5);
// BF: 中下 (x~0, y<0)
var dataBF = generateData(77, -2, 2, -6, -0.5);
// AF: 右下 (x>0, y<0)
var dataAF = generateData(74, 5, 40, -4, -0.5);

option = {
    title: {
        text: '散点图',
        left: 'center',
        top: 10,
        textStyle: {
            fontSize: 24,
            fontFamily: 'KaiTi' // 尝试匹配手写体风格
        }
    },
    tooltip: {
        trigger: 'item',
        formatter: function (params) {
            return params.seriesName + ': ' + params.value[0].toFixed(1) + ', ' + params.value[1].toFixed(1);
        }
    },
    legend: {
        data: ['CD', 'BD', 'AD', 'CF', 'BF', 'AF'],
        left: '10%',
        top: '15%',
        orient: 'vertical',
        itemWidth: 12,
        itemHeight: 12,
        textStyle: {
            fontSize: 14,
            color: '#333'
        }
    },
    grid: {
        left: '10%',
        right: '15%',
        bottom: '15%',
        top: '20%',
        containLabel: true
    },
    xAxis: {
        type: 'value',
        min: -50,
        max: 100,
        name: 'Centroid offset (mm)',
        nameLocation: 'middle',
        nameGap: 30,
        nameTextStyle: {
            fontSize: 16
        },
        axisLine: {
            lineStyle: { color: '#000' }
        },
        axisTick: { show: false },
        splitLine: {
            lineStyle: {
                type: 'dashed',
                color: '#ddd'
            }
        },
        axisLabel: {
            formatter: function (value) {
                if (value === -50) return '-50(C)';
                if (value === 0) return '0(B)';
                if (value === 50) return '50';
                if (value === 100) return '100(A)';
                return value;
            },
            fontSize: 14,
            color: '#000'
        },
        // 强制显示特定刻度
        axisPointer: { show: false }
    },
    yAxis: {
        type: 'value',
        min: -8,
        max: 10,
        name: 'Edge height difference (mm)',
        nameLocation: 'middle',
        nameGap: 50,
        nameRotate: 90,
        nameTextStyle: {
            fontSize: 16
        },
        axisLine: {
            lineStyle: { color: '#000' }
        },
        axisTick: { show: false },
        splitLine: {
            lineStyle: {
                type: 'dashed',
                color: '#ddd'
            }
        },
        axisLabel: {
            formatter: function (value) {
                if (value === 10) return '10(D)';
                if (value === 0) return '0(E)';
                if (value === -8) return '-8(F)';
                return value;
            },
            fontSize: 14,
            color: '#000'
        }
    },
    series: [
        {
            name: 'CD',
            type: 'scatter',
            symbolSize: 10,
            itemStyle: { color: colors.CD, opacity: 0.7 },
            data: dataCD
        },
        {
            name: 'BD',
            type: 'scatter',
            symbolSize: 10,
            itemStyle: { color: colors.BD, opacity: 0.9 },
            data: dataBD
        },
        {
            name: 'AD',
            type: 'scatter',
            symbolSize: 10,
            itemStyle: { color: colors.AD, opacity: 0.6 },
            data: dataAD
        },
        {
            name: 'CF',
            type: 'scatter',
            symbolSize: 10,
            itemStyle: { color: colors.CF, opacity: 0.8 },
            data: dataCF
        },
        {
            name: 'BF',
            type: 'scatter',
            symbolSize: 10,
            itemStyle: { color: colors.BF, opacity: 0.8 },
            data: dataBF
        },
        {
            name: 'AF',
            type: 'scatter',
            symbolSize: 10,
            itemStyle: { color: colors.AF, opacity: 0.7 },
            data: dataAF
        }
    ],
    // 使用 graphic 组件绘制右下角的统计表格
    graphic: [
        {
            type: 'group',
            right: '5%',
            bottom: '5%',
            children: [
                // 背景框
                {
                    type: 'rect',
                    left: 0,
                    top: 0,
                    width: 220,
                    height: 140,
                    style: {
                        fill: '#f5f5f5',
                        stroke: '#ccc',
                        lineWidth: 1
                    }
                },
                // 标题栏背景
                {
                    type: 'rect',
                    left: 0,
                    top: 0,
                    width: 220,
                    height: 30,
                    style: {
                        fill: '#999',
                        stroke: '#999'
                    }
                },
                // 标题文字
                {
                    type: 'text',
                    left: 'center',
                    top: 8,
                    style: {
                        text: 'Count & χ² Test',
                        fill: '#fff',
                        font: '14px sans-serif'
                    }
                },
                // 第一行数据: CD 35, BD 80, AD 146
                {
                    type: 'text',
                    left: 20,
                    top: 45,
                    style: {
                        text: '35',
                        fill: '#333',
                        font: '14px sans-serif',
                        textAlign: 'center'
                    }
                },
                {
                    type: 'text',
                    left: 80,
                    top: 45,
                    style: {
                        text: '80',
                        fill: '#333',
                        font: '14px sans-serif',
                        textAlign: 'center'
                    }
                },
                {
                    type: 'text',
                    left: 140,
                    top: 45,
                    style: {
                        text: '146',
                        fill: '#333',
                        font: '14px sans-serif',
                        textAlign: 'center'
                    }
                },
                // 第二行数据: CF 215, BF 77, AF 74
                {
                    type: 'text',
                    left: 20,
                    top: 75,
                    style: {
                        text: '215',
                        fill: '#333',
                        font: '14px sans-serif',
                        textAlign: 'center'
                    }
                },
                {
                    type: 'text',
                    left: 80,
                    top: 75,
                    style: {
                        text: '77',
                        fill: '#333',
                        font: '14px sans-serif',
                        textAlign: 'center'
                    }
                },
                {
                    type: 'text',
                    left: 140,
                    top: 75,
                    style: {
                        text: '74',
                        fill: '#333',
                        font: '14px sans-serif',
                        textAlign: 'center'
                    }
                },
                // 底部统计值
                {
                    type: 'text',
                    left: 20,
                    top: 110,
                    style: {
                        text: 'χ² = 508.458',
                        fill: '#333',
                        font: '14px sans-serif'
                    }
                },
                {
                    type: 'text',
                    left: 140,
                    top: 110,
                    style: {
                        text: 'P < 0.01',
                        fill: '#333',
                        font: '14px sans-serif'
                    }
                },
                // 装饰用的小圆点 (对应图例颜色)
                { type: 'circle', cx: 20, cy: 40, r: 4, style: { fill: colors.CD } },
                { type: 'circle', cx: 80, cy: 40, r: 4, style: { fill: colors.BD } },
                { type: 'circle', cx: 140, cy: 40, r: 4, style: { fill: colors.AD } },
                { type: 'circle', cx: 20, cy: 70, r: 4, style: { fill: colors.CF } },
                { type: 'circle', cx: 80, cy: 70, r: 4, style: { fill: colors.BF } },
                { type: 'circle', cx: 140, cy: 70, r: 4, style: { fill: colors.AF } }
            ]
        }
    ]
};

myChart.setOption(option);