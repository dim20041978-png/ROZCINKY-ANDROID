package ua.rozcinky.app;
public class PdfProvider extends android.content.ContentProvider {
 public boolean onCreate(){return true;}
 private java.io.File file(android.net.Uri uri)throws java.io.FileNotFoundException{String n=uri.getLastPathSegment();if(n==null||!n.matches("[A-Za-z0-9_-]+\\.pdf"))throw new java.io.FileNotFoundException();java.io.File f=new java.io.File(getContext().getFilesDir(),"reports/"+n);if(!f.isFile()&&n.startsWith("preview-"))f=new java.io.File(getContext().getCacheDir(),n);if(!f.isFile())throw new java.io.FileNotFoundException();return f;}
 public android.os.ParcelFileDescriptor openFile(android.net.Uri u,String mode)throws java.io.FileNotFoundException{if(!"r".equals(mode))throw new java.io.FileNotFoundException();return android.os.ParcelFileDescriptor.open(file(u),android.os.ParcelFileDescriptor.MODE_READ_ONLY);}
 public String getType(android.net.Uri u){return "application/pdf";}
 public android.database.Cursor query(android.net.Uri u,String[] projection,String selection,String[] args,String sort){try{java.io.File f=file(u);String[] cols=projection==null?new String[]{"_display_name","_size"}:projection;android.database.MatrixCursor c=new android.database.MatrixCursor(cols);Object[] row=new Object[cols.length];for(int i=0;i<cols.length;i++){if("_display_name".equals(cols[i]))row[i]=f.getName();if("_size".equals(cols[i]))row[i]=f.length();}c.addRow(row);return c;}catch(Exception e){return null;}}
 public android.net.Uri insert(android.net.Uri u,android.content.ContentValues v){throw new UnsupportedOperationException();}
 public int update(android.net.Uri u,android.content.ContentValues v,String s,String[] a){throw new UnsupportedOperationException();}
 public int delete(android.net.Uri u,String s,String[] a){throw new UnsupportedOperationException();}
}