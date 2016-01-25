//http://bootsnipp.com/snippets/featured/bootstrap-30-treeview
//http://jsfiddle.net/SeanWessell/roc0cqzc/


var openedClass = 'glyphicon-folder-open';
var closedClass = 'glyphicon-folder-close';

$.fn.extend({
    treed: function (o) {
      
      // var openedClass = 'glyphicon-minus-sign';
      // var closedClass = 'glyphicon-plus-sign';
      
      // if (typeof o != 'undefined'){
      //   if (typeof o.openedClass != 'undefined'){
      //   openedClass = o.openedClass;
      //   }
      //   if (typeof o.closedClass != 'undefined'){
      //   closedClass = o.closedClass;
      //   }
      // };
      
        //initialize each of the top levels
        var tree = $(this);
        tree.addClass("tree");
        tree.find('li').has("ul").each(function () {
            var branch = $(this); //li with children ul
            branch.prepend("<i class='indicator glyphicon " + closedClass + "'></i>");
            branch.addClass('branch');
            branch.on('click', function (e) {
                if (this == e.target) {
                    var icon = $(this).children('i:first');
                    icon.toggleClass(openedClass + " " + closedClass);
                    $(this).children().children().toggle();
                }
            })
            branch.children().children().toggle();
        });
        //fire event from the dynamically added icon
      tree.find('.branch .indicator').each(function(){
        $(this).on('click', function () {
            $(this).closest('li').click();
        });
      });
        //fire event to open branch if the li contains an anchor instead of text
        tree.find('.branch>a').each(function () {
            $(this).on('click', function (e) {
                $(this).closest('li').click();
                e.preventDefault();
            });
        });
        //fire event to open branch if the li contains a button instead of text
        tree.find('.branch>button').each(function () {
            $(this).on('click', function (e) {
                $(this).closest('li').click();
                e.preventDefault();
            });
        });
    }
});



function addBranchToTree(branch, branchName, treeType){
    if(treeType == 'test_case'){
        var onclick = "startAddNewTestCase(this)";
    }
    else{
        var onclick = "startAddNewPageObject(this)";
    }
    branch.html("<a href='#''>"+branchName+"</a> \
                    <ul> \
                        <li><i class='glyphicon glyphicon-plus-sign'></i> \
                            <a href='#' onclick='"+onclick+"'> Add New</a> \
                        </li> \
                    </ul>");
    branch.prepend("<i class='indicator glyphicon " + closedClass + "'></i>");
    branch.addClass('branch');
    branch.on('click', function (e) {
        if (this == e.target) {
            var icon = $(this).children('i:first');
            icon.toggleClass(openedClass + " " + closedClass);
            $(this).children().children().toggle();
        }
    })
    branch.children().children().toggle();

      //fire event from the dynamically added icon
      branch.find('.indicator').each(function(){
        $(this).on('click', function () {
            $(this).closest('li').click();
        });
      });
        //fire event to open branch if the li contains an anchor instead of text
        branch.find('a').each(function () {
            $(this).on('click', function (e) {
                $(this).closest('li').click();
                e.preventDefault();
            });
        });
        //fire event to open branch if the li contains a button instead of text
        branch.find('button').each(function () {
            $(this).on('click', function (e) {
                $(this).closest('li').click();
                e.preventDefault();
            });
        });
}