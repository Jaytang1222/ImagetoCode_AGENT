// 获取 DOM 容器
var chartDom = document.getElementById('main');
var myChart = echarts.init(chartDom);
var option;

// 辅助函数：生成正态分布的随机数
function randomNormal(mean, stdDev) {
    var u = 0, v = 0;
    while(u === 0) u = Math.random();
    while(v === 0) v = Math.random();
    return mean + stdDev * Math.sqrt( -2.0 * Math.log( u ) ) * Math.cos( 2.0 * Math.PI * v );
}

// 生成模拟数据，尽可能还原图中的分布形态
function generateData(count, xMean, xStd, yMean, yStd) {
    var data = [];
    for (var i = 0; i < count; i++) {
        var x = randomNormal(xMean, xStd);
        var y = randomNormal(yMean, yStd);
        // 限制范围以防溢出太多
        if (x > -60 && x < 110 && y > -9 && y < 11) {
            data.push([x, y]);
        }
    }
    return data;
}

// 定义颜色
var colors = {
    CD: '#8FD3F4', // 浅蓝
    BD: '#006D96', // 深蓝
    AD: '#B5E688', // 浅绿
    CF: '#1E90FF', // 中蓝
    BF: '#A9A9A9', // 灰色
    AF: '#FFDAB9'  // 浅橙
};

// 生成各组数据
// CD: 左上 (x<0, y>0)
var dataCD = generateData(35, -15, 10, 1.5, 1.5);
// BD: 中上 (x~0, y>0) - 垂直条状
var dataBD = generateData(80, 0, 1, 1.5, 2.5); 
// AD: 右上 (x>0, y>0) - 分布广
var dataAD = generateData(146, 30, 20, 3, 3);
// CF: 左下 (x<0, y<0)
var dataCF = generateData(215, -10, 8, -2, 2);
// BF: 中下 (x~0, y<0) - 垂直条状
var dataBF = generateData(77, 0, 1, -2.5, 2.5);
// AF: 右下 (x>0, y<0)
var dataAF = generateData(74, 15, 10, -1, 1.5);

option = {
    title: {
        text: '散点图',
        left: 'center',
        top: 0,
        textStyle: {
            fontSize: 24,
            fontFamily: 'KaiTi' // 尝试模仿手写体/楷体风格
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
        left: '15%',
        top: '10%',
        orient: 'vertical',
        textStyle: {
            fontSize: 14
        },
        itemWidth: 10,
        itemHeight: 10
    },
    grid: {
        left: '10%',
        right: '15%',
        top: '15%',
        bottom: '15%',
        containLabel: true
    },
    xAxis: {
        type: 'value',
        min: -50,
        max: 100,
        splitLine: {
            show: false
        },
        axisLine: {
            lineStyle: {
                color: '#333'
            }
        },
        axisLabel: {
            color: '#333',
            fontSize: 14,
            formatter: function (value) {
                if (value === -50) return '-50(C)';
                if (value === 0) return '0(B)';
                if (value === 50) return '50';
                if (value === 100) return '100(A)';
                return value;
            }
        },
        name: 'Centroid offset (mm)',
        nameLocation: 'middle',
        nameGap: 30,
        nameTextStyle: {
            fontSize: 16,
            fontWeight: 'bold'
        }
    },
    yAxis: {
        type: 'value',
        min: -8,
        max: 10,
        splitLine: {
            show: false
        },
        axisLine: {
            lineStyle: {
                color: '#333'
            }
        },
        axisLabel: {
            color: '#333',
            fontSize: 14,
            formatter: function (value) {
                if (value === 10) return '10(D)';
                if (value === 0) return '0(E)';
                if (value === -8) return '-8(F)';
                return value;
            }
        },
        name: 'Edge height difference (mm)',
        nameLocation: 'middle',
        nameGap: 50,
        nameTextStyle: {
            fontSize: 16,
            fontWeight: 'bold'
        },
        nameRotate: 90
    },
    series: [
        {
            name: 'CD',
            type: 'scatter',
            symbolSize: 10,
            itemStyle: { color: colors.CD },
            data: dataCD
        },
        {
            name: 'BD',
            type: 'scatter',
            symbolSize: 10,
            itemStyle: { color: colors.BD },
            data: dataBD
        },
        {
            name: 'AD',
            type: 'scatter',
            symbolSize: 10,
            itemStyle: { color: colors.AD },
            data: dataAD
        },
        {
            name: 'CF',
            type: 'scatter',
            symbolSize: 10,
            itemStyle: { color: colors.CF },
            data: dataCF
        },
        {
            name: 'BF',
            type: 'scatter',
            symbolSize: 10,
            itemStyle: { color: colors.BF },
            data: dataBF
        },
        {
            name: 'AF',
            type: 'scatter',
            symbolSize: 10,
            itemStyle: { color: colors.AF },
            data: dataAF
        }
    ],
    // 使用 graphic 组件绘制右下角的统计表格
    graphic: [
        {
            type: 'group',
            left: '65%',
            bottom: '18%',
            children: [
                // 背景框
                {
                    type: 'rect',
                    left: 0,
                    top: 0,
                    shape: { width: 220, height: 130 },
                    style: {
                        fill: '#E0E0E0',
                        stroke: '#999',
                        lineWidth: 1
                    }
                },
                // 标题
                {
                    type: 'text',
                    left: 'center',
                    top: 15,
                    style: {
                        text: 'Count & χ² Test',
                        font: '14px sans-serif',
                        fill: '#fff',
                        textAlign: 'center'
                    },
                    bounding: 'raw',
                    style: {
                        fill: '#fff',
                        backgroundColor: '#888', // 模拟表头背景
                        padding: [2, 10],
                        textAlign: 'center'
                    }
                     // 注意：ECharts graphic text 不支持直接的 backgroundColor 像 CSS 那样，这里用 rect 模拟表头更准确，但为了简化代码，直接画文字
                },
                 // 表头背景条 (修正)
                {
                    type: 'rect',
                    left: 0,
                    top: 0,
                    shape: { width: 220, height: 25 },
                    style: { fill: '#999' }
                },
                {
                    type: 'text',
                    left: 110,
                    top: 18,
                    style: {
                        text: 'Count & χ² Test',
                        font: '14px sans-serif',
                        fill: '#fff',
                        textAlign: 'center'
                    }
                },
                
                // 第一行数据: CD 35, BD 80, AD 146
                {
                    type: 'circle', left: 20, top: 45, shape: { r: 4 }, style: { fill: colors.CD }
                },
                { type: 'text', left: 35, top: 45, style: { text: '35', font: '12px sans-serif', fill: '#333', textAlign: 'left' } },
                
                {
                    type: 'circle', left: 90, top: 45, shape: { r: 4 }, style: { fill: colors.BD }
                },
                { type: 'text', left: 105, top: 45, style: { text: '80', font: '12px sans-serif', fill: '#333', textAlign: 'left' } },

                {
                    type: 'circle', left: 160, top: 45, shape: { r: 4 }, style: { fill: colors.AD }
                },
                { type: 'text', left: 175, top: 45, style: { text: '146', font: '12px sans-serif', fill: '#333', textAlign: 'left' } },

                // 第二行数据: CF 215, BF 77, AF 74
                {
                    type: 'circle', left: 20, top: 75, shape: { r: 4 }, style: { fill: colors.CF }
                },
                { type: 'text', left: 35, top: 75, style: { text: '215', font: '12px sans-serif', fill: '#333', textAlign: 'left' } },
                
                {
                    type: 'circle', left: 90, top: 75, shape: { r: 4 }, style: { fill: colors.BF }
                },
                { type: 'text', left: 105, top: 75, style: { text: '77', font: '12px sans-serif', fill: '#333', textAlign: 'left' } },

                {
                    type: 'circle', left: 160, top: 75, shape: { r: 4 }, style: { fill: colors.AF }
                },
                { type: 'text', left: 175, top: 75, style: { text: '74', font: '12px sans-serif', fill: '#333', textAlign: 'left' } },

                // 底部统计值
                {
                    type: 'text', left: 20, top: 105, style: { text: 'χ² = 508.458', font: '12px sans-serif', fill: '#333', textAlign: 'left' }
                },
                {
                    type: 'text', left: 150, top: 105, style: { text: 'P < 0.01', font: '12px sans-serif', fill: '#333', textAlign: 'left' }
                }
            ]
        },
        // 右下角水印
        {
            type: 'group',
            right: 10,
            bottom: 10,
            children: [
                {
                    type: 'text',
                    style: {
                        text: '博硕科研绘图',
                        font: '14px sans-serif',
                        fill: '#ccc',
                        textAlign: 'right'
                    }
                }
            ]
        }
    ]
};

// 添加辅助线 (X=0, Y=0)
// 由于 markLine 是系列级别的，我们给第一个系列添加，但设置全局生效或者给每个系列都加
// 这里为了简单，我们在 series 配置完后，通过 setOption 再次合并或者直接在 option 里配置
// 更好的方式是在 series 里统一配置 markLine，或者使用 xAxis/yAxis 的 splitLine 但颜色要改
// 观察原图，红线是贯穿的，且很细。
// 我们修改 xAxis 和 yAxis 的 splitLine 来实现网格线，但原图只有 X=0 和 Y=0 是红线。
// 使用 markLine 在任意一个系列上配置即可。

option.series[0].markLine = {
    symbol: 'none',
    lineStyle: {
        color: '#FFA07A', // 浅红色/鲑鱼色，接近原图
        width: 1,
        type: 'dashed'
    },
    data: [
        { xAxis: 0 },
        { yAxis: 0 }
    ]
};

myChart.setOption(option);