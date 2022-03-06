clear all;
close all;
clc;

warning('off','all');

Set=1;
Vid=[1,2,3,4,5,7,8];% 1 2 x3 4 x5 7 8 x9   x1 2 x4 5 6 7 8
%Sec=20:1:60;
calTileVal = 0;

% for baseline
nGridR = 6;
nGridC = 12;

nExtra = 10; % 除了baseline的22-42 QP作为Pano的限制外，还可以增加size更大的限制
%nExtraBSL = 1;
% sumSize_PanoAve = zeros(1,42-22+1+nExtraPano);
% PSPNR_PanoAve = zeros(1,42-22+1+nExtraPano);
% sumSize_BSLAve = zeros(1,42-22+1);
% PSPNR_BSLAve = zeros(1,42-22+1);
AllSumSize_Pano = [];
AllPSPNR_Pano = [];
AllSumSize_BSL = [];
AllPSPNR_BSL = [];
%viewportQPsizePerGrid_PanoAve = zeros(1,42-22+1);
%viewportQPsizePerGrid_BSLAve = zeros(1,42-22+1);
for set=Set
    for vid=Vid
        mkdir(['randSecs/',num2str(set)]);
        if ~exist(['randSecs/',num2str(set),'/',num2str(vid),'.mat'],'file')
            Sec = 20+randperm(40);
            Sec = sort(Sec(1:10));
            save(['randSecs/',num2str(set),'/',num2str(vid),'.mat'],'Sec');
        else
            Sec = cell2mat(struct2cell(load(['randSecs/',num2str(set),'/',num2str(vid),'.mat'])));
        end
        
        mkdir(['baselineResult/',num2str(nGridR),'_',num2str(nGridC),'/',num2str(set),'/',num2str(vid)]);
        mkdir(['PanoResult/',num2str(set),'/',num2str(vid)]);
        for sec=Sec
            %% 如果chunk存在问题，跳过
            try
                secString=sprintf('%03d',sec-1);
                vr=VideoReader(['videos/',num2str(set),'/',num2str(vid),'/',secString,'.mp4']);
                if vr.Duration~=1
                    continue;
                end
                secString=sprintf('%03d',sec-2);
                vr=VideoReader(['videos/',num2str(set),'/',num2str(vid),'/',secString,'.mp4']);
                if vr.Duration~=1
                    continue;
                end
            catch
                continue;
            end
            
            
            %DEBUG
            if calTileVal
                calcTileValueness(set,vid,sec);
                continue;
            end
            
            
            if ~exist(['baselineResult/',num2str(nGridR),'_',num2str(nGridC),'/',num2str(set),'/',num2str(vid),'/',num2str(sec),'.mat'])
                [PSPNR_BSL,sumSize_BSL,sumViewedTilesArea_BSL,viewportQPsizePerGrid_BSL] = baseline(set,vid, sec, nGridR, nGridC);
                save(['baselineResult/',num2str(nGridR),'_',num2str(nGridC),'/',num2str(set),'/',num2str(vid),'/',num2str(sec),'.mat'],'PSPNR_BSL','sumSize_BSL','sumViewedTilesArea_BSL','viewportQPsizePerGrid_BSL');
            else
                load(['baselineResult/',num2str(nGridR),'_',num2str(nGridC),'/',num2str(set),'/',num2str(vid),'/',num2str(sec),'.mat']);
            end
            
            %DEBUG
            %continue;
            
            if ~exist(['PanoResult/',num2str(set),'/',num2str(vid),'/',num2str(sec),'.mat'])
                % PSPNR_Pano = zeros(48,42-22+1);
                % sumSize_Pano = zeros(48,42-22+1);
                [PSPNR_Pano, sumSize_Pano,sumViewedTilesArea_Pano,viewportQPsizePerGrid_Pano] = Pano(set,vid,sec,2880/24,1440/12,sumSize_BSL,nExtra);
                %                 PSPNR_Pano(:,qp-22+1) = tempPSPNR';
                %                 sumSize_Pano(:,qp-22+1) = tempSumSize';
                
                save(['PanoResult/',num2str(set),'/',num2str(vid),'/',num2str(sec),'.mat'],'PSPNR_Pano','sumSize_Pano','sumViewedTilesArea_Pano','viewportQPsizePerGrid_Pano');
            else
                load(['PanoResult/',num2str(set),'/',num2str(vid),'/',num2str(sec),'.mat']);
            end
            
            
            %             plot(22:42,viewportQPsizePerGrid_Pano,'g');
            %             hold on;
            %             plot(22:42,viewportQPsizePerGrid_BSL,'r');
            
            %viewportQPsizePerGrid_PanoAve(qp-22+1) = viewportQPsizePerGrid_PanoAve(qp-22+1)+viewportQPsizePerGrid_Pano(qp-22+1);
            %viewportQPsizePerGrid_BSLAve(qp-22+1) = viewportQPsizePerGrid_BSLAve(qp-22+1)+viewportQPsizePerGrid_BSL(qp-22+1);
            for user=1:48
                [sumSize_BSL_user,index] = sort(sumSize_BSL(user,:),'ascend');
                AllSumSize_BSL=[AllSumSize_BSL;sumSize_BSL_user];
                AllPSPNR_BSL=[AllPSPNR_BSL;PSPNR_BSL(user,index)];
                
                [sumSize_Pano_user,index] = sort(sumSize_Pano(user,:),'ascend');
                AllSumSize_Pano=[AllSumSize_Pano;sumSize_Pano_user];
                AllPSPNR_Pano=[AllPSPNR_Pano;PSPNR_Pano(user,index)];
            end
        end
    end
end

%% DEBUG
% sumSize_PanoAve = sumSize_PanoAve(1:21);
% PSPNR_PanoAve = PSPNR_PanoAve(1:21);
% sumSize_BSLAve = sumSize_BSLAve(1:21);
% PSPNR_BSLAve = PSPNR_BSLAve(1:21);

%%
if 0
    ssBS = mean(AllSumSize_BSL(:,1));
    ssBE = mean(AllSumSize_BSL(:,42-22+1));
    ssPS = mean(AllSumSize_Pano(:,1));
    ssPE = mean(AllSumSize_Pano(:,42-22+1+nExtra));
    pB=zeros(1,20);
    pBn=zeros(1,20);
    pP=zeros(1,20);
    pPn=zeros(1,20);
    for i=1:size(AllSumSize_BSL,1)
        for j=1:42-22+1
            range=max(1,ceil((AllSumSize_BSL(i,j)-AllSumSize_BSL(i,1))/(AllSumSize_BSL(i,42-22+1)-AllSumSize_BSL(i,1))*20));
            pB(range) = pB(range)+AllPSPNR_BSL(i,j);
            pBn(range) = pBn(range)+1;
        end
    end
    for i=1:size(AllSumSize_Pano,1)
        for j=1:42-22+1+nExtra
            range=max(1,ceil((AllSumSize_Pano(i,j)-AllSumSize_Pano(i,1))/(AllSumSize_Pano(i,42-22+1+nExtra)-AllSumSize_Pano(i,1))*20));
            pP(range) = pP(range)+AllPSPNR_Pano(i,j);
            pPn(range) = pPn(range)+1;
        end
    end
    pB = pB./pBn;
    pP = pP./pPn;
    
    
    plot(ssBS+(0.5:1:19.5)*(ssBE-ssBS)/20,pB,'r');
    hold on;
    plot(ssPS+(0.5:1:19.5)*(ssPE-ssPS)/20,pP,'g');
else
    plot(mean(AllSumSize_BSL),mean(AllPSPNR_BSL),'r');
    hold on;
    plot(mean(AllSumSize_Pano),mean(AllPSPNR_Pano),'g');
end
%xlim([500 5000]);

%viewportQPsizePerGrid_PanoAve = viewportQPsizePerGrid_PanoAve/nAve;
%viewportQPsizePerGrid_BSLAve = viewportQPsizePerGrid_BSLAve/nAve;
% plot(22:42,viewportQPsizePerGrid_PanoAve,'g');
% hold on;
% plot(22:42,viewportQPsizePerGrid_BSLAve,'r');