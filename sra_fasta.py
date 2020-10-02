#!/usr/bin/env python

import sys, argparse, vdb

def fastq_from_tbl( args, tbl ) :
    acc = args.accession[ 0 ]
    
    col_names = [ "READ" ]
    if args.split :
        col_names.append( "READ_START" )
        col_names.append( "READ_LEN" )
    cols = tbl.CreateCursor().OpenColumns( col_names )
    
    c_read = cols[ col_names[ 0 ] ]
    if args.split :
        c_read_start = cols[ col_names[ 1 ] ]
        c_read_len   = cols[ col_names[ 2 ] ]
    
    first, count = c_read.row_range()
    
    if args.first != None :
        first = args.first[ 0 ]
    if args.count != None :
        count = args.count[ 0 ]

    fasta = b'>i\n{0}\n'
    for row in range( first, first + count ) :
        read     = c_read.Read( row )
        rd_start = c_read_start.Read( row )
        rd_len   = c_read_len.Read( row )
        for x in range( 0, len( rd_start ) ) :
            rlen  = rd_len[ x ]
            if rlen > 0 :
                start = rd_start[ x ]
                end   = start + rlen
                print(f">i\n{read[start:end].decode('utf-8')}")

    
if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument( 'accession', nargs='*' )    
    parser.add_argument( '-X', '--first', metavar='row-id', help='first row-id', nargs=1, type=int, dest='first' )
    parser.add_argument( '-N', '--count', metavar='rows', help='how many reads', nargs=1, type=int, dest='count' )
    parser.add_argument( '--split', help='split spot', action='store_true' )
    args = parser.parse_args()
    
    try :
        #open a manager in read-mode ( dflt-mode )
        mgr = vdb.manager()
        
        for acc in args.accession :
            #detect path-type ( database or table or anything-else )
            pt = mgr.PathType( acc )
            if pt == vdb.PathType.Database :
                #object is a database
                fastq_from_tbl( args, mgr.OpenDB( acc ).OpenTable( "SEQUENCE" ) )
            elif pt == vdb.PathType.Table :
                #object is a table
                fastq_from_tbl( args, mgr.OpenTable( acc ) )
            else :
                print( "%s is not an SRA-object"%( acc ) )
    except vdb.vdb_error as e :
        print( e )
    except KeyboardInterrupt :
        print( "^C" )
