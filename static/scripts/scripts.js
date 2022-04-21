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
    request.send("table="+table+"&id="+record_id+"&vote_number="+String(vote_number+change_vote_by)+'&vote='+vote);
}

function mark_answer(status, answer_id, question_id){
    const request = new XMLHttpRequest();
    let current_status = document.getElementById('accept_'+answer_id).innerHTML
    if (current_status == 'Accept'){
        document.getElementById('accept_'+answer_id).innerHTML = 'Unaccept'
        document.getElementById(answer_id).style.backgroundColor = 'var(--cardbg_accepted)'
        document.getElementById('accept_mark_'+answer_id).innerHTML = '<i class="fa fa-check"></i>'
    } else {
        document.getElementById('accept_'+answer_id).innerHTML = 'Accept'
        document.getElementById(answer_id).style.backgroundColor = 'var(--cardbg)'
        document.getElementById('accept_mark_'+answer_id).innerHTML = ''
    }
    console.log(current_status)
    request.open("POST","/test-accept-answer");
    request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    request.send("status="+status+"&answer_id="+answer_id+"&question_id="+question_id);
}

