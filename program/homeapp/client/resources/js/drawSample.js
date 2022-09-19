App.drawSample = (function () {
    // 绘制打印效果示例图
    var start = function (font_color, font_size) {

        var canvas = document.getElementById('myCanvas');
        canvas.width = canvas.width;
        if (!canvas.getContext) return;
        var ctx = canvas.getContext("2d");
        // 绘制矩形
        ctx.strokeRect(33, 20, 330, 228);
        // 绘制折痕线
        ctx.beginPath(); //新建一条path
        ctx.setLineDash([1, 1, 3, 3, 1, 4, 4, 1], 0);
        ctx.moveTo(33, 210); //把画笔移动到指定的坐标
        ctx.lineTo(363, 210);  //绘制一条从当前位置到指定坐标(200, 50)的直线.
        //闭合路径。会拉一条从当前点到path起始点的直线。如果当前点与起始点重合，则什么都不做
        ctx.closePath();
        ctx.stroke(); //绘制路径。

        //写文字
        switch (font_color) {
            case 'blue':
                ctx.fillStyle = "rgb(0, 0, 255)";  //蓝色
                break;
            case 'golden':
                ctx.fillStyle = "rgb(255, 215, 0)";  //金色
                break;
            default:
                ctx.fillStyle = "rgb(0,0,0)";  //黑色
                break;
        }

            ctx.font = "30px simhei";
            ctx.fillText("公司", 50, 60);
            ctx.fillText("职位", 280, 180);
            ctx.textAlign = "center";
            switch (font_size) {
                case '140':
                    ctx.font = "75px simhei";
                    break;
                case '120':
                    ctx.font = "65px simhei";
                    break;
                default:
                    ctx.font = "70px simhei";
                    break;
            }
            ctx.fillText("姓名", 200, 130);


    }
    return {
        start: start,
    };
})();