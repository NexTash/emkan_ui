$(document).ready(function() {
    
    setTimeout(function() {        
        $(".list-row-col .level-item[data-sort-by='title']").each(function() {            
            if ($(this).text().trim() === "Title") {
            console.log("777");
                $(this).text("Name");
            }
        });
    }, 300);
});
