
 let arr_en = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'];
 let arr_EN = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'];
 let arr_symb = ['!', '@', '#', '$', '%', '&', '?', '-', '+', '=', '~'];
 let arr_num = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"];
 let arr_symbName = ['@', '$', '&','-'];

function checkPasswordMastContain(word) {

    for (let i = 0; i < word.length; i++) {
        if (arr_en.indexOf(word[i]) >= 0){
            for (let b = 0; b < word.length; b++) {
                if (arr_EN.indexOf(word[b]) >= 0) {
                    for (let s = 0; s < word.length; s++) {
                        if (arr_symb.indexOf(word[s]) >= 0) {
                            for (let c = 0; c < word.length; c++) {
                                if (arr_num.indexOf(word[c]) >= 0 ) {
                                    return false;
                                }
                            }
                        }
                    }
                } 
            }
        }
    }
    return true;
}

function checkPasswordInvalidSymbol(word) {

    for (let i = 0; i < word.length; i++) {
            if (arr_en.indexOf(word[i]) === -1){
                if (arr_EN.indexOf(word[i]) === -1) {        
                    if (arr_symb.indexOf(word[i]) === -1){          
                        if (arr_num.indexOf(word[i]) === -1) {
                            console.log(word[i])
                            return true;
                        }   
                    }
                }  
            }
        }
        return false;    
}


 function checkUsernameInvalidSymbol(word) {

    for (let i = 0; i < word.length; i++) {
        if (arr_en.indexOf(word[i]) === -1){
            if (arr_EN.indexOf(word[i]) === -1) {        
                if (arr_symbName.indexOf(word[i]) === -1){          
                    if (arr_num.indexOf(word[i]) === -1) {
                        return true;
                    }   
                }
            }  
        }
    }
    return false;    
}