function extractSignalDimension(sys)
    % Load model
    load_system(sys);
    % Open output file
    fid = fopen('dimensions.txt','w');
    try
        % Compile model
        eval([sys,'([],[],[],''compile'')']); 

        % Get top-level inports and outports separately
        inports = find_system(sys, 'SearchDepth', 1, 'BlockType', 'Inport');
        outports = find_system(sys, 'SearchDepth', 1, 'BlockType', 'Outport');

        % Write model name explicitly
        fprintf(fid, 'ModelName:%s\n', sys);

        % Record top-level inputs explicitly
        for i = 1:length(inports)
            ph = get_param(inports{i}, 'PortHandles');
            pdim = get_param(ph.Outport, 'CompiledPortDimensions');
            fprintf(fid, 'ModelInput,%s\n', get_param(inports{i},'Name'));
            fprintf(fid, '%d\n', pdim(1));
            fprintf(fid, '%d\n', pdim(2:end));
        end

        % Record top-level outputs explicitly
        for i = 1:length(outports)
            ph = get_param(outports{i}, 'PortHandles');
            pdim = get_param(ph.Inport, 'CompiledPortDimensions');
            fprintf(fid, 'ModelOutput,%s\n', get_param(outports{i},'Name'));
            fprintf(fid, '%d\n', pdim(1));
            fprintf(fid, '%d\n', pdim(2:end));
        end

        % Then, handle subsystems and other blocks
        blocks = find_system(sys, 'Type', 'block');
        for i = 1:numel(blocks)
            fullname = getfullname(blocks{i});
            pnum = get_param(blocks{i}, 'Ports');
            ph = get_param(blocks{i}, 'PortHandles');

            % Skip top-level inports/outports (already processed)
            if ismember(blocks{i}, [inports; outports])
                continue;
            end

            % Process input ports
            for j = 1:pnum(1)
                pdim = get_param(ph.Inport(j), 'CompiledPortDimensions');
                fprintf(fid, '%s,IN,%d\n', fullname, j);
                fprintf(fid, '%d\n', pdim(1));
                fprintf(fid, '%d\n', pdim(2:end));
            end

            % Process output ports
            for j = 1:pnum(2)
                pdim = get_param(ph.Outport(j), 'CompiledPortDimensions');
                fprintf(fid, '%s,OUT,%d\n', fullname, j);
                fprintf(fid, '%d\n', pdim(1));
                fprintf(fid, '%d\n', pdim(2:end));
            end
        end
    catch ME
        disp(['compile error: ', ME.message]);
    end

    % Terminate compilation
    eval([sys,'([],[],[],''term'')']);
    fclose(fid);
    close_system(sys);
end
