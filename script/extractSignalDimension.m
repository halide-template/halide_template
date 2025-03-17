function extractSignalDimension(sys)
    % Load model
    load_system(sys);
    % Open output file
    fid = fopen('dimensions.txt','w');
    try
        % Compile model
        eval([sys,'([],[],[],''compile'')']); 
        % Get all blocks
        obj = find_system(sys, 'Type','block');  
        for i=1:numel(obj)  
            % Get name, port numbers, and port handlers
            fullname = getfullname(obj{i});
            pnum = get_param(obj{i},'Ports');
            ph = get_param(obj{i},'PortHandles');

            % Process each input port
            inph = ph.Inport; 
            for j=1:pnum(1)
                pdim = get_param(inph(j),'CompiledPortDimensions');
                dimCount = pdim(1);
                dimSizes = pdim(2:end);
                
                % Output to command window
                disp([fullname ',IN,' num2str(j)]);
                disp(dimSizes);
                
                % Write to file
                fprintf(fid,'%s,%s,%d\n',fullname,'IN',j);
                fprintf(fid,'%d\n',dimCount); % 写入维度个数
                fprintf(fid,'%d\n',dimSizes); % 逐行写入每个维度大小
            end
           
            % Process each output port
            outph = ph.Outport;
            for j=1:pnum(2)
                pdim = get_param(outph(j),'CompiledPortDimensions');
                dimCount = pdim(1);
                dimSizes = pdim(2:end);
                
                % Output to command window
                disp([fullname ',OUT,' num2str(j)]);
                disp(dimSizes);
                
                % Write to file
                fprintf(fid,'%s,%s,%d\n',fullname,'OUT',j);
                fprintf(fid,'%d\n',dimCount); % 写入维度个数
                fprintf(fid,'%d\n',dimSizes); % 逐行写入每个维度大小
            end
        end
    catch ME
        disp(['compile error: ', ME.message]);
    end
    % Terminate compilation
    eval([sys,'([],[],[],''term'')']);
    % Close file and model
    fclose(fid);
    close_system(sys);
end
