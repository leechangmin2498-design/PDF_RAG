window.onload=function(){
    
        CompanyDisplay.style.display = 'none';

        fieldset_rel.style.display = 'none';

        AbilityUnitFieldSet.style.display = 'none';
       
   
}



function searchFuntion(){
    var CompanyDisplay=document.getElementById("CompanyDisplay");
    // if(CompanyDisplay.style.display=='none'){
    //     CompanyDisplay.style.display = 'block';
    // }else{
    //     CompanyDisplay.style.display = 'none';
    // }
    if(CompanyDisplay.style.display=='none'){
        CompanyDisplay.style.display = 'block';
    }
}

function fieldfuntion(){
    var fieldset_rel=document.getElementById("fieldset_rel");
    if(fieldset_rel.style.display=='none'){
        fieldset_rel.style.display = 'block';
    }
}

function AbilityUnitFieldFun(){
    var AbilityUnitFieldSet=document.getElementById("AbilityUnitFieldSet");
    
    if(AbilityUnitFieldSet.style.display=='none'){
        AbilityUnitFieldSet.style.display = 'block';
    }
}