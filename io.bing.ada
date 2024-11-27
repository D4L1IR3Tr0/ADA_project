-- IO Library for ADA

define exists(path):
    out(__internal_exists(path))
/.

define create_file(path):
    int handle <- __internal_create(path)
    bool success <- handle >= 0
    
    if (success):
        __internal_close(handle)
        write("File created successfully")
    else:
        write("Failed to create file")
    /.
    
    out(success)
/.

define write_file(path, content):
    bool success <- __internal_write_file(path, content)
    
    if (success):
        write("Content written successfully")
    else:
        write("Failed to write to file")
    /.
    
    out(success)
/.

define read_file(path):
    bool file_exists <- __internal_exists(path)  -- Utiliser directement la fonction interne
    if (!file_exists):
        write("Error: File does not exist: " + path)
        out("")
    /.
    
    string content <- __internal_read_file(path)
    out(content)
/.

define append_file(path, content):
    bool success <- __internal_append_file(path, content)
    
    if (success):
        write("Content appended successfully")
    else:
        write("Failed to append to file")
    /.
    
    out(success)
/.

define delete_file(path):
    bool file_exists <- __internal_exists(path)  -- Utiliser directement la fonction interne
    if (!file_exists):
        write("Error: File does not exist: " + path)
        out(false)
    /.
    
    bool success <- __internal_delete(path)
    if (success):
        write("File deleted successfully")
    else:
        write("Failed to delete file")
    /.
    
    out(success)
/.

define file_size(path):
    bool file_exists <- __internal_exists(path)  -- Utiliser directement la fonction interne
    if (!file_exists):
        write("Error: File does not exist: " + path)
        out(-1)
    /.
    
    out(__internal_size(path))
/.