function drawTable(div, tHead, tData, data_len, page, pageNum, file_path){
    if(page)
    {
        createDivpage(div, pageNum, file_path);
    }
    else
    {
        var table = document.createElement("table");
        var tbody = document.createElement("tbody");
        table.appendChild(tbody);
        var tr = tbody.insertRow(0);
        for (var i = 0; i < tHead.length; i++)
        {
            var th = document.createElement("th");
            th.innerHTML = tHead[i];
            tr.appendChild(th);
        }
        for (var i = 0; i < data_len; i++)
        {
            var tr = tbody.insertRow(tbody.rows.length);
            for (var j = 0; j < tData.length; j++)
            {
                var td = tr.insertCell(tr.cells.length);
                td.innerHTML = tData[j][i];
            }
        }
        table.setAttribute("class","bordered");
        div.insertBefore(table, div.children[0]);
    }
};

function createDivpage(mainDiv, pageNum, file_path)
{
    var pagDiv = document.createElement("div");
    pagDiv.style.textAlign = "right";
    pagDiv.style.paddingTop = "2%";
    pagDiv.style.paddingBottom = "5px";
    // pagDiv.id = mainDiv.id + "pagiDiv";
    var idList = ["spanFirst","spanPre","spanNext","spanLast"];
    for(var i = 0; i<idList.length; i++)
    {
        var spanTmp = document.createElement("span");
        spanTmp.id = mainDiv.id + idList[i];
        spanTmp.style.background = "#1e90ff";
        spanTmp.style.borderRadius = ".2em";
        spanTmp.style.padding = "5px";
        spanTmp.style.margin = "2px";                
        pagDiv.appendChild(spanTmp);
    }

    var currPageSpan = document.createElement("span");
    pagDiv.appendChild(currPageSpan);
    var currPageNum;

    const textNode_1 = document.createTextNode("第");
    pagDiv.insertBefore(textNode_1, pagDiv.children[4]);
    const textNode_2 = document.createTextNode("页/总"+pageNum.toString()+"页");
    pagDiv.insertBefore(textNode_2, null);
    mainDiv.appendChild(pagDiv);

    //页面标签变量

    var preSpan = document.getElementById(mainDiv.id + "spanPre");
    var firstSpan = document.getElementById(mainDiv.id + "spanFirst");
    var nextSpan = document.getElementById(mainDiv.id + "spanNext");
    var lastSpan = document.getElementById(mainDiv.id + "spanLast");
    firstPage(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path);
}

function updateTable(file_path, mainDiv, pageIndex)
{
    $.getJSON('/nmas/page_request/',{file:file_path, pageIndex:pageIndex, item:mainDiv.id},function(ret){
        if(ret.filed == "error")
        {
            alert(ret.data);
        }
        else
        {
            var thead = ret.filed;
            var tdata = ret.data;
            var len = ret.data[0].length;
            if(mainDiv.children.length > 1)
            {
                mainDiv.removeChild(mainDiv.childNodes[0]);
            }
            drawTable(mainDiv, thead, tdata, len, false, 0, null);
        }        
    })
    .fail(function(){alert("请求数据已失效");});
}

function firstPage(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path){
    currPageNum = 1;
    showCurrPage(currPageNum, currPageSpan);
    updateTable(file_path, mainDiv, currPageNum);
    firstText(firstSpan);
    preText(preSpan);
    if(pageNum == 1)
    {
        nextText(nextSpan);
        lastText(lastSpan);
    }
    else
    {
        nextLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path);
        lastLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path);
    }        
}

function prePage(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path){
    currPageNum--;
    showCurrPage(currPageNum, currPageSpan);
    updateTable(file_path, mainDiv, currPageNum);
    if(1 == currPageNum){
        firstText(firstSpan);
        preText(preSpan);
        nextLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path);
        lastLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path);
    }else if(pageNum == currPageNum){
        preLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path);
        firstLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path);
        nextText(nextSpan);
        lastText(lastSpan);
    }else{
        firstLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path);
        preLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path);
        nextLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path);
        lastLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path);
    }

}

function nextPage(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path){
    currPageNum++;
    showCurrPage(currPageNum, currPageSpan);
    updateTable(file_path, mainDiv, currPageNum);

    if(1 == currPageNum){
        firstText(firstSpan);
        preText(preSpan);
        nextLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path);
        lastLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path);
    }else if(pageNum == currPageNum){
        preLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path);
        firstLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path);
        nextText(nextSpan);
        lastText(lastSpan);
    }else{
        firstLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path);
        preLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path);
        nextLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path);
        lastLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path);
    }
}

function lastPage(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path){
    currPageNum = pageNum;
    showCurrPage(currPageNum, currPageSpan);
    updateTable(file_path, mainDiv, currPageNum);
    firstLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path);
    preLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path);
    nextText(nextSpan);
    lastText(lastSpan);
}


function showCurrPage(currPageNum, currPageSpan){
    currPageSpan.innerHTML = currPageNum;
}


//控制首页等功能的显示与不显示
function firstLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path){
    firstSpan.innerHTML = "首页";
    firstSpan.style.cursor = "pointer";
    firstSpan.style.textDecoration = "underline";
    firstSpan.style.color = "#DCDCDC";
    firstSpan.onclick=function(){
        firstPage(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path)
    };
}
function firstText(firstSpan){
    firstSpan.innerHTML = "首页";
    firstSpan.style.cursor = "";
    firstSpan.style.textDecoration = "";
    firstSpan.style.color = "";
    firstSpan.onclick = null;
}

function preLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path){
    preSpan.innerHTML = "上一页";
    preSpan.style.cursor = "pointer";
    preSpan.style.textDecoration = "underline";
    preSpan.style.color = "#DCDCDC";
    preSpan.onclick=function(){
        prePage(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path)
    };
}
function preText(preSpan){
    preSpan.innerHTML = "上一页";
    preSpan.style.cursor = "";
    preSpan.style.textDecoration = "";
    preSpan.style.color = "";
    preSpan.onclick=null;
}

function nextLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path){
    nextSpan.innerHTML = "下一页";
    nextSpan.style.cursor = "pointer";
    nextSpan.style.textDecoration = "underline";
    nextSpan.style.color = "#DCDCDC";
    nextSpan.onclick=function(){
        nextPage(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path)
    };
}
function nextText(nextSpan){
    nextSpan.innerHTML = "下一页";
    nextSpan.style.cursor = "";
    nextSpan.style.textDecoration = "";
    nextSpan.style.color = "";
    nextSpan.onclick=null;
}

function lastLink(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path){
    lastSpan.innerHTML = "末页";
    lastSpan.style.cursor = "pointer";
    lastSpan.style.textDecoration = "underline";
    lastSpan.style.color = "#DCDCDC";
    lastSpan.onclick=function(){
        lastPage(mainDiv, currPageNum, pageNum, firstSpan, preSpan, nextSpan, lastSpan, currPageSpan, file_path)
    };
}
function lastText(lastSpan){
    lastSpan.innerHTML = "末页";
    lastSpan.style.cursor = "";
    lastSpan.style.textDecoration = "";
    lastSpan.style.color = "";
    lastSpan.onclick = null;
}