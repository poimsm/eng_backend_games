#!/bin/bash

case "$(uname -s)" in    
    CYWGWIN*|MSYS*|MINGW*)
        echo 'Windows'
        winpty docker exec -it games_django bash    
    ;;

    *)
        echo 'Linux'
        docker exec -it games_django bash
    ;;
esac
