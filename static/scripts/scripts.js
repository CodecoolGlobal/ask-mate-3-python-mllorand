function vote_on_record(table, record_id, vote){
    let change_vote_by
    if(vote === 'down'){
        change_vote_by = -1
    } else {
        change_vote_by = 1
    }
    const vote_number = parseInt(document.getElementById(table+'_vote_number_'+record_id).innerHTML)
    document.getElementById(table+'_vote_number_'+record_id).innerHTML = String(vote_number+change_vote_by);
    const request = new XMLHttpRequest();
    request.open("POST","/vote_on_record");
    request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    request.send("table="+table+"&id="+record_id+"&vote_number="+String(vote_number+change_vote_by));
}
