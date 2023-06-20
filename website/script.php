<?php
    //get the i, n, b, e and m parameters from URL
    $i=$_GET["i"];
    $n=$_GET["n"];
    $b=$_GET["b"];
    $e=$_GET["e"];
    $m=$_GET["m"];

    //verify if the parameters are not empty
    if($i == "" || $n == "" || $b == "" || $e == "" || $m == ""){
        echo "Error: Empty parameters";
        return;
    }
    
    //execute python script in Path : ../Script Python Chat GPT/Automatic-Product-Completion.py
    $command = escapeshellcmd('python ../Script\ Python\ Chat\ GPT/Automatic-Product-Completion.py -i \"'.$i.'\" -n \"'.$n.'\" -b \"'.$b.'\" -e \"'.$e. '\" -m \"'.$m.'\"');
    $output = shell_exec($command);
    echo $output;

    //Get all the content text files in directory ../Script Python Chat GPT/Products/$i and diplay them in index.html
    $files = glob('../Script Python Chat GPT/Products/'.$i.'/*'); // get all file names
    //display the content of the text files
    foreach($files as $file){
        //verify if the file is a text file
        $ext = pathinfo($file, PATHINFO_EXTENSION);
        if($ext != "txt"){
            continue;
        }
        $content = file_get_contents($file);
        //Diplay the content in index.html
        echo "<p>".$content."</p>";
    }
    
    //get all the images in directory ../Script Python Chat GPT/Products/$i/img and display them in index.html
    $files = glob('../Script Python Chat GPT/Products/'.$i.'/img/*'); // get all file names
    //display the images
    foreach($files as $file){
        //verify if the file is an image
        $ext = pathinfo($file, PATHINFO_EXTENSION);
        if($ext != "jpg" && $ext != "png" && $ext != "jpeg"){
            continue;
        }
        //Display the image in index.html
        echo "<img src=\"".$file."\" alt=\"".$file."\" width=\"auto\" height=\"auto\">";
    }

?>